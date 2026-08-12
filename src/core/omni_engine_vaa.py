import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

SLIPPAGE_BPS = 10 / 10000

def run_vaa():
    print("[*] Downloading VAA Universe Data...")
    offensive = ['SPY', 'EFA', 'EEM', 'AGG']
    defensive = ['LQD', 'IEF', 'SHY']
    tickers = offensive + defensive
    
    # AGG inception 2003, EEM 2003
    df = yf.download(tickers, start="2005-01-01", end="2024-01-01")['Close']
    df = df[~df.index.duplicated(keep='first')]
    df = df.ffill().dropna()
    
    returns = df.pct_change().dropna()
    
    # Calculate Momentum Score: 12 * 1M + 4 * 3M + 2 * 6M + 1 * 12M
    # We will use 21, 63, 126, 252 days
    p0 = df
    p1 = df.shift(21)
    p3 = df.shift(63)
    p6 = df.shift(126)
    p12 = df.shift(252)
    
    score = 12 * (p0 / p1 - 1) + 4 * (p0 / p3 - 1) + 2 * (p0 / p6 - 1) + 1 * (p0 / p12 - 1)
    
    df['YearMonth'] = df.index.to_period('M')
    month_ends = df.groupby('YearMonth').tail(1).index
    
    weights = pd.DataFrame(np.nan, index=df.index, columns=tickers)
    
    for date in month_ends:
        if date not in score.index or pd.isna(score.loc[date, 'SPY']):
            continue
            
        for col in tickers:
            weights.loc[date, col] = 0.0
            
        # VAA Logic
        # Check offensive scores
        off_scores = score.loc[date, offensive]
        if isinstance(off_scores, pd.DataFrame):
            off_scores = off_scores.iloc[0]
            
        def_scores = score.loc[date, defensive]
        if isinstance(def_scores, pd.DataFrame):
            def_scores = def_scores.iloc[0]
            
        if (off_scores < 0).any(): # If ANY offensive asset is < 0
            # Risk OFF: 100% into best defensive asset
            best_def = def_scores.idxmax()
            weights.loc[date, best_def] = 1.0
        else:
            # Risk ON: 100% into best offensive asset
            best_off = off_scores.idxmax()
            weights.loc[date, best_off] = 1.0

    weights = weights.ffill().shift(1).fillna(0.0)
    
    valid_idx = returns.index.intersection(weights.index)[252:]
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
    print(f"[*] VIGILANT ASSET ALLOCATION (VAA) RESULTS")
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

if __name__ == "__main__":
    run_vaa()
