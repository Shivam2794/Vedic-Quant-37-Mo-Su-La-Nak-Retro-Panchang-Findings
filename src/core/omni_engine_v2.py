import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

SLIPPAGE_BPS = 10 / 10000

def run_independent_vol_target_momentum():
    print("[*] Downloading Asset-Level Volatility Targeting Data...")
    tickers = ['SPY', 'TLT', 'GLD', 'DBC', 'VNQ', 'EFA', 'EEM', 'LQD', 'HYG', 'SHV']
    df = yf.download(tickers, start="2008-01-01", end="2024-01-01", auto_adjust=False)['Close']
    df = df[~df.index.duplicated(keep='first')]
    df = df.ffill().dropna()
    
    returns = df.pct_change().dropna()
    
    # 20-day annualized volatility per asset
    vol20 = returns.rolling(20).std() * np.sqrt(252)
    
    # 6-month Momentum
    mom6 = df.pct_change(126)
    
    TARGET_VOL = 0.10 # 10% Volatility target per asset
    
    df['YearMonth'] = df.index.to_period('M')
    month_ends = df.groupby('YearMonth').tail(1).index
    
    assets = ['SPY', 'TLT', 'GLD', 'DBC', 'VNQ', 'EFA', 'EEM', 'LQD', 'HYG']
    weights = pd.DataFrame(np.nan, index=df.index, columns=tickers)
    
    for date in month_ends:
        if date not in vol20.index or date not in mom6.index:
            continue
            
        for col in tickers:
            weights.loc[date, col] = 0.0 # explicit 0 instead of nan
        cash_weight = 1.0
        
        for asset in assets:
            m6 = mom6.loc[date, asset]
            v20 = vol20.loc[date, asset]
            if isinstance(m6, pd.Series):
                m6 = m6.iloc[0]
            if isinstance(v20, pd.Series):
                v20 = v20.iloc[0]
                
            if pd.isna(m6) or pd.isna(v20) or v20 == 0:
                continue
                
            # Dual Momentum: Must be positive to hold
            if m6 > 0:
                # Volatility Target scaling
                w = TARGET_VOL / v20
                w = min(w, 0.25) # Cap individual asset weight at 25% (since we have 9 assets)
                
                weights.loc[date, asset] = w
                cash_weight -= w
        
        weights.loc[date, 'SHV'] = cash_weight

    weights = weights.ffill().shift(1).fillna(0.0)
    
    valid_idx = returns.index.intersection(weights.index)[126:]
    weights = weights.loc[valid_idx]
    r = returns.loc[valid_idx]
    
    port_ret = (weights * r).sum(axis=1)
    
    # Turnover calculation
    delta = pd.Series(0.0, index=weights.index)
    rebalance_dates = [d for d in month_ends if d in weights.index]
    for i in range(1, len(rebalance_dates)):
        curr = rebalance_dates[i]
        prev = rebalance_dates[i-1]
        delta.loc[curr] = (weights.loc[curr] - weights.loc[prev]).abs().sum()
        
    port_ret -= (delta * SLIPPAGE_BPS)
    
    cagr = (1 + port_ret).prod() ** (252 / len(port_ret)) - 1
    sharpe = np.sqrt(252) * port_ret.mean() / (port_ret.std() + 1e-9)
    
    cum_ret = (1 + port_ret).cumprod()
    max_dd = ((cum_ret - cum_ret.cummax()) / cum_ret.cummax()).min()
    annual_turnover = delta.sum() * 252 / len(port_ret)
    
    print("========================================================")
    print(f"[*] ASSET-LEVEL VOL-TARGETED DUAL MOMENTUM RESULTS")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    print(f"Annual Turnover: {annual_turnover:.2f}x")
    
    # Benchmark SPY
    spy = r['SPY'] if isinstance(r, pd.DataFrame) else r
    bm_cagr = (1 + spy).prod() ** (252 / len(spy)) - 1
    bm_sharpe = np.sqrt(252) * spy.mean() / (spy.std() + 1e-9)
    bm_max_dd = (((1 + spy).cumprod() - (1 + spy).cumprod().cummax()) / (1 + spy).cumprod().cummax()).min()
    print(f"[*] SPY BENCHMARK CAGR: {bm_cagr:.2%} | Sharpe: {bm_sharpe:.2f} | Max DD: {bm_max_dd:.2%}")
    print("========================================================")
    return port_ret

if __name__ == "__main__":
    ret = run_independent_vol_target_momentum()
