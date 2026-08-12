import pandas as pd
import numpy as np
import optuna
import datetime
import warnings
import json
import requests
import time
import re
import traceback
warnings.filterwarnings('ignore')
optuna.logging.set_verbosity(optuna.logging.WARNING)

API_KEY = "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"

# ============================================================
# BACKTEST ENGINE (Strictly corrected)
# ============================================================
TZ = 'America/New_York'
SLIPPAGE_BPS = 0.0010
TQQQ_LEVERAGE = 3.0
TARGET_VOL_ANNUAL = 0.60
MAX_POSITION_PCT = 0.50

def load_data():
    qqq_d = pd.read_parquet('qqq_daily.parquet')
    qqq_1m = pd.read_parquet('qqq_1m.parquet')
    tqqq_1m = pd.read_parquet('tqqq_1m.parquet')
    for df in [qqq_d, qqq_1m, tqqq_1m]:
        df.index = pd.to_datetime(df.index).tz_convert(TZ)
    qqq_1m = qqq_1m.between_time('09:30', '15:59')
    tqqq_1m = tqqq_1m.between_time('09:30', '15:59')
    tqqq_1m = tqqq_1m[(tqqq_1m['Volume'] > 0)]
    qqq_1m = qqq_1m[qqq_1m['Volume'] > 0]
    return qqq_d, qqq_1m, tqqq_1m

def build_features(qqq_d, qqq_1m, tqqq_1m):
    d = qqq_d.copy()
    ret = d['Close'].pct_change()
    d['Vol_21'] = ret.rolling(21).std() * np.sqrt(252)
    d['Vol_5'] = ret.rolling(5).std() * np.sqrt(252)
    d['GEX_Regime'] = np.where(d['Vol_5'] < d['Vol_21'], 1, -1)
    
    # ATR
    hl = d['High'] - d['Low']
    hc = (d['High'] - d['Close'].shift(1)).abs()
    lc = (d['Low'] - d['Close'].shift(1)).abs()
    d['ATR'] = pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(14).mean()
    d['ATR_pct'] = d['ATR'] / d['Close']
    
    # RSI
    delta = d['Close'].diff()
    d['RSI'] = 100 - (100 / (1 + (delta.where(delta > 0, 0).rolling(14).mean() / (-delta.where(delta < 0, 0).rolling(14).mean()).replace(0, 1e-10))))
    
    # MAs
    d['SMA_20'] = d['Close'].rolling(20).mean()
    d['SMA_50'] = d['Close'].rolling(50).mean()
    d['Dist_SMA20'] = (d['Close'] / d['SMA_20']) - 1.0
    
    for c in ['Close', 'Volume', 'ATR_pct', 'RSI', 'GEX_Regime', 'Vol_21', 'Dist_SMA20']:
        d[f'Prev_{c}'] = d[c].shift(1)
        
    d['date_str'] = d.index.strftime('%Y-%m-%d')
    daily_feats = d.dropna().set_index('date_str')
    
    # Intraday
    qqq_1m = qqq_1m.copy()
    tqqq_1m = tqqq_1m.copy()
    qqq_1m['date_str'] = qqq_1m.index.strftime('%Y-%m-%d')
    tqqq_1m['date_str'] = tqqq_1m.index.strftime('%Y-%m-%d')
    qqq_1m['hour'] = qqq_1m.index.hour
    qqq_1m['minute'] = qqq_1m.index.minute
    tqqq_1m['hour'] = tqqq_1m.index.hour
    tqqq_1m['minute'] = tqqq_1m.index.minute

    def get_b(df, h, m, c, rn):
        return df[(df['hour'] == h) & (df['minute'] == m)].groupby('date_str').first()[[c]].rename(columns={c: rn})

    q_930 = get_b(qqq_1m, 9, 30, 'Open', 'QQQ_Open_930')
    q_1000 = get_b(qqq_1m, 10, 0, 'Open', 'QQQ_Open_1000')
    q_1030 = get_b(qqq_1m, 10, 30, 'Close', 'QQQ_Close_1030')
    q_1500 = get_b(qqq_1m, 15, 0, 'Close', 'QQQ_Close_1500')
    
    t_1031 = get_b(tqqq_1m, 10, 31, 'Open', 'TQQQ_Entry_1031')
    t_1501 = get_b(tqqq_1m, 15, 1, 'Open', 'TQQQ_Entry_1501')
    t_1558 = get_b(tqqq_1m, 15, 58, 'Close', 'TQQQ_Exit_1558')
    t_last = tqqq_1m.groupby('date_str').tail(1).groupby('date_str')['Close'].last().rename('TQQQ_LastClose')
    
    id_hl = tqqq_1m[((tqqq_1m['hour'] == 10) & (tqqq_1m['minute'] > 30)) | ((tqqq_1m['hour'] > 10) & (tqqq_1m['hour'] < 15)) | ((tqqq_1m['hour'] == 15) & (tqqq_1m['minute'] <= 58))].groupby('date_str').agg({'High':'max', 'Low':'min'})
    id_hl.columns = ['ID_High', 'ID_Low']
    
    lk = q_930.join(q_1000).join(q_1030).join(q_1500).join(t_1031).join(t_1501).join(t_1558).join(t_last).join(id_hl)
    signal_df = lk.join(daily_feats).dropna()
    return signal_df

def compute_metrics(daily_pnl):
    if len(daily_pnl) < 50:
        return {'Sharpe': -999, 'MaxDD': -999, 'CAGR': -999, 'Trades': 0}
    cum = (1 + daily_pnl).cumprod()
    yrs = ((pd.to_datetime(str(daily_pnl.index[-1])) - pd.to_datetime(str(daily_pnl.index[0]))).days / 365.25)
    if yrs < 0.1: return {'Sharpe': -999, 'MaxDD': -999, 'CAGR': -999, 'Trades': 0}
    cagr = cum.iloc[-1] ** (1.0 / yrs) - 1
    ann_vol = daily_pnl.std() * np.sqrt(252)
    sharpe = cagr / ann_vol if ann_vol > 1e-10 else -999
    max_dd = ((cum / cum.cummax()) - 1).min()
    trades = (daily_pnl != 0).sum()
    return {'Sharpe': sharpe, 'MaxDD': max_dd, 'CAGR': cagr, 'Trades': trades}

# ============================================================
# LLM QUERY ENGINE
# ============================================================
def query_fable(prompt):
    data = {
        "model": "~anthropic/claude-fable-latest",
        "max_tokens": 8000,
        "messages": [
            {"role": "system", "content": "You are an elite AI Quant. Return ONLY python code enclosed in ```python...```. No other text."},
            {"role": "user", "content": prompt}
        ]
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": "https://localhost",
        "X-Title": "Agentic Loop",
        "Content-Type": "application/json"
    }
    for attempt in range(3):
        try:
            r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=60)
            if r.status_code == 200:
                txt = r.json()['choices'][0]['message']['content']
                m = re.search(r'```python\n(.*?)```', txt, re.DOTALL)
                return m.group(1) if m else txt
            else:
                print(f"API Error {r.status_code}: {r.text}")
                time.sleep(5)
        except Exception as e:
            print(f"Request failed: {e}")
            time.sleep(5)
    return None

# ============================================================
# AGENTIC LOOP
# ============================================================
PROMPT_TEMPLATE = """
We are running an eternal Optuna strategy search. We need a COMPLETELY UNIQUE strategy archetype for TQQQ.
We have a signal dataframe `signal_df` with columns:
['QQQ_Open_930', 'QQQ_Open_1000', 'QQQ_Close_1030', 'QQQ_Close_1500',
 'TQQQ_Entry_1031', 'TQQQ_Entry_1501', 'TQQQ_Exit_1558', 'TQQQ_LastClose', 
 'ID_High', 'ID_Low', 'Prev_ATR_pct', 'Prev_RSI', 'Prev_GEX_Regime', 
 'Prev_Vol_21', 'Prev_Dist_SMA20']

Constraints you MUST follow to survive 10 BPS slip:
- Use vectorization. Return a pd.Series of daily PnL (index=date_str).
- Use `TQQQ_Entry_1031` or `TQQQ_Entry_1501` as entry prices.
- Multiply entry price by (1 + 0.0010) and exit by (1 - 0.0010) for 10 BPS slippage.
- Use `Prev_Vol_21` for sizing: `size = np.minimum(0.5, 0.60 / np.maximum(df['Prev_Vol_21']*3.0, 0.05))`
- DO NOT short TQQQ. Long only.
- MUST TRADE FREQUENTLY! You must target at least 300 trades over the 3-year backtest (~2 trades/week). Strategies with rare triggers are useless. Do NOT make the gating conditions too strict.

Write TWO functions:
def get_optuna_params(trial):
    # return a dict of param choices (limit to 3-6 params to keep search fast)
    return {
        'threshold': trial.suggest_float('threshold', 0.0, 0.02),
        # etc...
    }

def strategy_logic(df, params):
    # df is signal_df. Compute mask.
    # Compute PnL. return pnl_series

{history}

Write the python code now:
"""

def main():
    print("Loading data...")
    qqq_d, qqq_1m, tqqq_1m = load_data()
    signal_df = build_features(qqq_d, qqq_1m, tqqq_1m)
    
    history_log = "PREVIOUS FAILED IDEAS:\n"
    
    for iteration in range(1, 1000):
        print(f"\n================ ITERATION {iteration} ================")
        prompt = PROMPT_TEMPLATE.replace("{history}", history_log[-2000:])
        
        print("Brainstorming via Fable...")
        code = query_fable(prompt)
        if not code:
            print("Fable API failed. Retrying...")
            continue
            
        with open("current_fable_strategy.py", "w") as f:
            f.write(code)
            
        print("Evaluating generated strategy...")
        
        try:
            # Dynamic import
            namespace = {}
            exec(code, namespace)
            get_params = namespace['get_optuna_params']
            strat_logic = namespace['strategy_logic']
            
            def objective(trial):
                p = get_params(trial)
                pnl = strat_logic(signal_df, p)
                m = compute_metrics(pnl)
                
                penalty = 0.0
                if m['MaxDD'] < -0.30: penalty += (-0.30 - m['MaxDD']) * 300
                if m['Trades'] < 300: penalty += (300 - m['Trades']) * 0.1
                return m['Sharpe'] - penalty

            study = optuna.create_study(direction='maximize', sampler=optuna.samplers.TPESampler())
            study.optimize(objective, n_trials=300, n_jobs=-1, show_progress_bar=False)
            
            best = study.best_params
            best_pnl = strat_logic(signal_df, best)
            m = compute_metrics(best_pnl)
            
            print(f"Idea resulted in Sharpe: {m['Sharpe']:.2f}, MaxDD: {m['MaxDD']*100:.2f}%")
            
            if m['Sharpe'] > 1.8 and m['MaxDD'] > -0.30 and m['Trades'] >= 300:
                print("\n GOAL ACHIEVED! ")
                with open("FINAL_WINNING_STRATEGY.py", "w") as f:
                    f.write(code)
                with open("FINAL_PARAMS.json", "w") as f:
                    json.dump(best, f, indent=4)
                break
            else:
                history_log += f"- Idea {iteration}: Max Sharpe {m['Sharpe']:.2f}. Failed.\n"
                
        except Exception as e:
            err = traceback.format_exc()
            print(f"Code execution failed:\n{err}")
            history_log += f"- Idea {iteration} crashed with error: {str(e)[:200]}\n"
            
if __name__ == "__main__":
    main()
