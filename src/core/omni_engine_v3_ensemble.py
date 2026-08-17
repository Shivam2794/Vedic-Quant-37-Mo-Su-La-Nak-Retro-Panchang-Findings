import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

SLIPPAGE_BPS = 10 / 10000

def rsi(series, period=2):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=period-1, adjust=False).mean()
    ema_down = down.ewm(com=period-1, adjust=False).mean()
    rs = ema_up / ema_down
    return 100 - (100 / (1 + rs))

def run_omni_ensemble():
    print("[*] Downloading Data for Omni-Ensemble...")
    tickers = ['UPRO', 'TMF', 'SPY', 'SHV']
    df = yf.download(tickers, start="2010-01-01", end="2024-01-01", auto_adjust=False)['Close']
    df = df[~df.index.duplicated(keep='first')]
    df = df.ffill().dropna()
    
    returns = df.pct_change().dropna()
    
    # ---------------------------------------------------------
    # STRATEGY 1: Volatility-Targeted Hedgefundie (Target Vol 15%)
    # ---------------------------------------------------------
    upro_w = 0.55
    tmf_w = 0.45
    
    base_hf_ret = returns['UPRO'] * upro_w + returns['TMF'] * tmf_w
    hf_vol20 = base_hf_ret.rolling(20).std() * np.sqrt(252)
    
    TARGET_VOL = 0.10 # Lower target to suppress drawdown
    
    df['YearMonth'] = df.index.to_period('M')
    month_ends = df.groupby('YearMonth').tail(1).index
    
    hf_weights = pd.DataFrame(np.nan, index=df.index, columns=['UPRO', 'TMF', 'SHV'])
    
    for date in month_ends:
        if date not in hf_vol20.index: continue
        cv = hf_vol20.loc[date]
        if isinstance(cv, pd.Series): cv = cv.iloc[0]
        if pd.isna(cv) or cv == 0: continue
            
        mult = TARGET_VOL / cv
        mult = min(mult, 1.0) # No margin
        
        hf_weights.loc[date, 'UPRO'] = upro_w * mult
        hf_weights.loc[date, 'TMF'] = tmf_w * mult
        hf_weights.loc[date, 'SHV'] = 1.0 - mult

    hf_weights = hf_weights.ffill().shift(1).fillna(0.0)
    
    # ---------------------------------------------------------
    # STRATEGY 2: High-Winrate Mean Reversion (Swing Trading)
    # ---------------------------------------------------------
    spy = df['SPY']
    if isinstance(spy, pd.DataFrame): spy = spy.iloc[:, 0]
        
    sma200 = spy.rolling(200).mean()
    sma5 = spy.rolling(5).mean()
    rsi2 = rsi(spy, 2)
    
    ma20 = spy.rolling(20).mean()
    std20 = spy.rolling(20).std()
    lower_bb = ma20 - (2 * std20)
    
    swing_weights = pd.Series(0.0, index=df.index)
    in_position = False
    
    for i in range(len(df)):
        date = df.index[i]
        if pd.isna(sma200.iloc[i]): continue
            
        if in_position and spy.iloc[i] > sma5.iloc[i]:
            in_position = False
            
        if not in_position and spy.iloc[i] < lower_bb.iloc[i] and rsi2.iloc[i] < 5 and spy.iloc[i] > sma200.iloc[i]:
            in_position = True
            
        if in_position:
            swing_weights.loc[date] = 1.0

    swing_weights = swing_weights.shift(1).fillna(0.0)
    
    # ---------------------------------------------------------
    # COMBINE ENSEMBLE (50% / 50%)
    # ---------------------------------------------------------
    valid_idx = returns.index.intersection(hf_weights.index).intersection(swing_weights.index)[200:]
    hf_weights = hf_weights.loc[valid_idx]
    swing_weights = swing_weights.loc[valid_idx]
    r = returns.loc[valid_idx]
    
    # HF Return Stream
    hf_delta = hf_weights.diff().abs().sum(axis=1).fillna(0)
    hf_ret = (hf_weights['UPRO'] * r['UPRO']) + (hf_weights['TMF'] * r['TMF']) + (hf_weights['SHV'] * (0.02/252))
    hf_ret -= (hf_delta * SLIPPAGE_BPS)
    
    # Swing Return Stream
    swing_delta = swing_weights.diff().abs().fillna(0)
    spy_r = r['SPY']
    if isinstance(spy_r, pd.DataFrame): spy_r = spy_r.iloc[:, 0]
    swing_ret = (swing_weights * spy_r) + ((1.0 - swing_weights) * (0.02/252))
    swing_ret -= (swing_delta * SLIPPAGE_BPS)
    
    # Final Portfolio
    port_ret = (hf_ret * 0.5) + (swing_ret * 0.5)
    
    # Apply 1.4x Leverage to the Entire Ensemble to maximize returns while hugging the 20% DD constraint
    LEVERAGE = 1.4
    borrow_cost = 0.02 / 252 # Assume 2% borrow rate for the leveraged portion
    
    port_ret = port_ret * LEVERAGE - (LEVERAGE - 1.0) * borrow_cost
    
    cagr = (1 + port_ret).prod() ** (252 / len(port_ret)) - 1
    sharpe = np.sqrt(252) * port_ret.mean() / (port_ret.std() + 1e-9)
    
    cum_ret = (1 + port_ret).cumprod()
    max_dd = ((cum_ret - cum_ret.cummax()) / cum_ret.cummax()).min()
    
    print("========================================================")
    print(f"[*] OMNI-ENSEMBLE (HF Vol-Target + Mean Reversion) RESULTS")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    
    # Benchmark SPY
    bm_cagr = (1 + spy_r).prod() ** (252 / len(spy_r)) - 1
    bm_sharpe = np.sqrt(252) * spy_r.mean() / (spy_r.std() + 1e-9)
    bm_max_dd = (((1 + spy_r).cumprod() - (1 + spy_r).cumprod().cummax()) / (1 + spy_r).cumprod().cummax()).min()
    print(f"[*] SPY BENCHMARK CAGR: {bm_cagr:.2%} | Sharpe: {bm_sharpe:.2f} | Max DD: {bm_max_dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_omni_ensemble()
