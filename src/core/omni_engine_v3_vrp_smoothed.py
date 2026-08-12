import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

SLIPPAGE_BPS = 10 / 10000

def run_vrp_smoothed():
    print("[*] Downloading Volatility Data (VIX, VIX3M, SVXY, SHV)...")
    tickers = ['^VIX', '^VIX3M', 'SVXY', 'SHV']
    
    df = yf.download(tickers, start="2012-01-01", end="2024-01-01")['Close']
    df = df[~df.index.duplicated(keep='first')]
    df = df.ffill().dropna()
    
    returns = df.pct_change().dropna()
    
    term_structure = df['^VIX'] / df['^VIX3M']
    
    # Smooth the term structure ratio with a 5-day SMA to prevent noise-based whip-saws
    # But react immediately if the RAW signal spikes above 1.0 (backwardation = instant panic)
    ts_sma = term_structure.rolling(5).mean()
    
    weights = pd.DataFrame(0.0, index=df.index, columns=['SVXY', 'SHV'])
    
    for i in range(len(df)):
        date = df.index[i]
        
        raw_ts = term_structure.iloc[i]
        sma_ts = ts_sma.iloc[i]
        
        if pd.isna(sma_ts):
            weights.loc[date, 'SHV'] = 1.0
            continue
            
        # VRP Logic V2:
        # Rule 1: Absolute Panic -> Raw ratio > 1.0 = Cash immediately
        # Rule 2: Trend Contango -> Smoothed ratio < 0.95 = Short Vol (SVXY)
        # Rule 3: Middle Ground -> Cash
        
        if raw_ts > 1.0:
            weights.loc[date, 'SHV'] = 1.0
        elif sma_ts < 0.95: 
            weights.loc[date, 'SVXY'] = 1.0
        else:
            weights.loc[date, 'SHV'] = 1.0

    # Prevent look-ahead bias
    weights = weights.shift(1).fillna(0.0)
    
    valid_idx = returns.index.intersection(weights.index)
    weights = weights.loc[valid_idx]
    r = returns.loc[valid_idx]
    
    # Assuming SHV yields roughly 2% annually / 252 for cash days
    r_shv = 0.02 / 252
    
    svxy_r = r['SVXY']
    if isinstance(svxy_r, pd.DataFrame): svxy_r = svxy_r.iloc[:, 0]
        
    port_ret = (weights['SVXY'] * svxy_r) + (weights['SHV'] * r_shv)
    
    # Turnover calculation (daily)
    delta = weights.diff().abs().sum(axis=1).fillna(0)
    
    # Apply Brutal Slippage
    port_ret -= (delta * SLIPPAGE_BPS)
    
    cagr = (1 + port_ret).prod() ** (252 / len(port_ret)) - 1
    sharpe = np.sqrt(252) * port_ret.mean() / (port_ret.std() + 1e-9)
    
    cum_ret = (1 + port_ret).cumprod()
    max_dd = ((cum_ret - cum_ret.cummax()) / cum_ret.cummax()).min()
    annual_turnover = delta.sum() * 252 / len(port_ret)
    
    print("========================================================")
    print(f"[*] VOLATILITY RISK PREMIUM (SMOOTHED) RESULTS")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    print(f"Annual Turnover: {annual_turnover:.2f}x")
    
    # Benchmark SPY
    spy = yf.download('SPY', start="2012-01-01", end="2024-01-01")['Close'].pct_change().dropna()
    spy = spy.loc[valid_idx]
    if isinstance(spy, pd.DataFrame): spy = spy.iloc[:, 0]
    bm_cagr = (1 + spy).prod() ** (252 / len(spy)) - 1
    bm_sharpe = np.sqrt(252) * spy.mean() / (spy.std() + 1e-9)
    bm_max_dd = (((1 + spy).cumprod() - (1 + spy).cumprod().cummax()) / (1 + spy).cumprod().cummax()).min()
    print(f"[*] SPY BENCHMARK CAGR: {bm_cagr:.2%} | Sharpe: {bm_sharpe:.2f} | Max DD: {bm_max_dd:.2%}")
    print("========================================================")
    
    return port_ret

if __name__ == "__main__":
    run_vrp_smoothed()
