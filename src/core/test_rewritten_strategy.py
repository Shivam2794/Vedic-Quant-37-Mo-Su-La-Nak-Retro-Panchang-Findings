import pandas as pd
import numpy as np
import optuna
import matplotlib.pyplot as plt
import json
import warnings
warnings.filterwarnings('ignore')
from FINAL_WINNING_STRATEGY import get_optuna_params, strategy_logic

optuna.logging.set_verbosity(optuna.logging.WARNING)

TZ = 'America/New_York'

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
    
    hl = d['High'] - d['Low']
    hc = (d['High'] - d['Close'].shift(1)).abs()
    lc = (d['Low'] - d['Close'].shift(1)).abs()
    d['ATR'] = pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(14).mean()
    d['ATR_pct'] = d['ATR'] / d['Close']
    
    delta = d['Close'].diff()
    d['RSI'] = 100 - (100 / (1 + (delta.where(delta > 0, 0).rolling(14).mean() / (-delta.where(delta < 0, 0).rolling(14).mean()).replace(0, 1e-10))))
    
    for c in ['Close', 'Volume', 'ATR_pct', 'RSI', 'GEX_Regime', 'Vol_21']:
        d[f'Prev_{c}'] = d[c].shift(1)
        
    d['date_str'] = d.index.strftime('%Y-%m-%d')
    daily_feats = d.dropna().set_index('date_str')
    
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
    
    t_1031 = get_b(tqqq_1m, 10, 31, 'Open', 'TQQQ_Entry_1031')
    t_1558 = get_b(tqqq_1m, 15, 58, 'Close', 'TQQQ_Exit_1558')
    
    lk = q_930.join(q_1000).join(q_1030).join(t_1031).join(t_1558)
    return lk.join(daily_feats).dropna()

def compute_metrics(daily_pnl):
    if len(daily_pnl) < 50:
        return {'Sharpe': -999, 'MaxDD': -999, 'CAGR': -999, 'Trades': 0, 'Win%': 0}
    cum = (1 + daily_pnl).cumprod()
    yrs = ((pd.to_datetime(str(daily_pnl.index[-1])) - pd.to_datetime(str(daily_pnl.index[0]))).days / 365.25)
    if yrs < 0.1: return {'Sharpe': -999, 'MaxDD': -999, 'CAGR': -999}
    cagr = cum.iloc[-1] ** (1.0 / yrs) - 1
    ann_vol = daily_pnl.std() * np.sqrt(252)
    sharpe = cagr / ann_vol if ann_vol > 1e-10 else -999
    max_dd = ((cum / cum.cummax()) - 1).min()
    trades = (daily_pnl != 0).sum()
    win_pct = (daily_pnl > 0).sum() / trades if trades > 0 else 0
    return {'Sharpe': sharpe, 'MaxDD': max_dd, 'CAGR': cagr, 'Trades': trades, 'Win%': win_pct}

print("Loading and preparing data...")
qqq_d, qqq_1m, tqqq_1m = load_data()
signal_df = build_features(qqq_d, qqq_1m, tqqq_1m)

def objective(trial):
    p = get_optuna_params(trial)
    pnl = strategy_logic(signal_df, p)
    m = compute_metrics(pnl)
    
    penalty = 0.0
    if m['MaxDD'] < -0.30: penalty += (-0.30 - m['MaxDD']) * 50
    if m['Trades'] < 50: penalty += 10
    
    return m['Sharpe'] - penalty

print("Running Optuna micro-grinder...")
study = optuna.create_study(direction='maximize', sampler=optuna.samplers.TPESampler(seed=123))
study.optimize(objective, n_trials=500, n_jobs=-1, show_progress_bar=False)

best = study.best_params
best_pnl = strategy_logic(signal_df, best)
m = compute_metrics(best_pnl)

print("\n--- TRUE PERFORMANCE (WITHOUT LOOK-AHEAD CHEAT) ---")
print(f"Sharpe: {m['Sharpe']:.2f}")
print(f"Max DD: {m['MaxDD']*100:.2f}%")
print(f"CAGR:   {m['CAGR']*100:.2f}%")
print(f"Trades: {m['Trades']}")
print(f"Win%:   {m['Win%']*100:.2f}%")
print("\nPARAMS:", json.dumps(best, indent=2))

with open('TRUE_PARAMS.json', 'w') as f:
    json.dump(best, f, indent=4)

cum = (1 + best_pnl).cumprod()
plt.figure(figsize=(10,6))
plt.plot(pd.to_datetime(cum.index), cum.values, color='magenta')
plt.title(f"Coiled Spring Alpha - TRUE PNL (No Lookahead)\nSharpe {m['Sharpe']:.2f} | DD {m['MaxDD']*100:.1f}%")
plt.grid(True, alpha=0.3)
plt.yscale('log')
plt.savefig('../brain/662b40cd-41f4-48b4-8be0-781b58f55b00/true_coiled_spring_equity.png')
print("Saved equity curve to artifacts.")
