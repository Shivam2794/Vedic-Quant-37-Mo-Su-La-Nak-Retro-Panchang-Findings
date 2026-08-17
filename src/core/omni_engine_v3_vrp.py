import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

SLIPPAGE_BPS = 10 / 10000

def run_vrp_arbitrage():
    print("[*] Downloading Volatility Data (VIX, VIX3M, SVXY, SHV)...")
    tickers = ['^VIX', 'SVXY', 'SHV']
    
    # SVXY inception is late 2011, we will start testing in 2012
    df = yf.download(tickers, start="2012-01-01", end="2024-01-01", auto_adjust=False)['Close']
    df = df[~df.index.duplicated(keep='first')]
    df = df.ffill().dropna()
    
    returns = df.pct_change().dropna()
    
    # Calculate VIX Term Structure Ratio
    # Contango: VIX < VIX3M (Ratio < 1.0) -> Normal regime, short vol is profitable
    # Backwardation: VIX > VIX3M (Ratio > 1.0) -> Panic regime, short vol gets destroyed
    
    term_structure = df['^VIX'] / df['^VIX'].rolling(60).mean()
    
    weights = pd.DataFrame(0.0, index=df.index, columns=['SVXY', 'SHV'])
    
    for i in range(len(df)):
        date = df.index[i]
        
        # We need yesterday's data to avoid look-ahead bias
        # The shift at the end handles this, so we compute based on current row
        ts = term_structure.iloc[i]
        
        if pd.isna(ts):
            weights.loc[date, 'SHV'] = 1.0
            continue
            
        # VRP Logic
        # We use a smoothed signal to avoid whip-saws
        # Let's just use raw daily state for maximum responsiveness to crashes
        if ts < 0.95: 
            # Deep Contango: Risk On (Short Volatility)
            weights.loc[date, 'SVXY'] = 1.0
        else:
            # Flat or Backwardation: Panic (Cash)
            weights.loc[date, 'SHV'] = 1.0

    # Prevent look-ahead bias (signals generated at close execute at next day's close)
    weights = weights.shift(1).fillna(0.0)
    
    valid_idx = returns.index.intersection(weights.index)
    weights = weights.loc[valid_idx]
    r = returns.loc[valid_idx]
    
    # Assuming SHV yields roughly 2% annually / 252 for cash days
    r_shv = 0.02 / 252
    
    port_ret = (weights['SVXY'] * r['SVXY']) + (weights['SHV'] * r_shv)
    
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
    print(f"[*] VOLATILITY RISK PREMIUM (VRP) ARBITRAGE RESULTS")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    print(f"Annual Turnover: {annual_turnover:.2f}x")
    
    # Benchmark SPY
    spy = yf.download('SPY', start="2012-01-01", end="2024-01-01", auto_adjust=False)['Close'].pct_change().dropna()
    spy = spy.loc[valid_idx]
    if isinstance(spy, pd.DataFrame): spy = spy.iloc[:, 0]
    bm_cagr = (1 + spy).prod() ** (252 / len(spy)) - 1
    bm_sharpe = np.sqrt(252) * spy.mean() / (spy.std() + 1e-9)
    bm_max_dd = (((1 + spy).cumprod() - (1 + spy).cumprod().cummax()) / (1 + spy).cumprod().cummax()).min()
    print(f"[*] SPY BENCHMARK CAGR: {bm_cagr:.2%} | Sharpe: {bm_sharpe:.2f} | Max DD: {bm_max_dd:.2%}")
    print("========================================================")
    
    return port_ret

if __name__ == "__main__":
    run_vrp_arbitrage()
