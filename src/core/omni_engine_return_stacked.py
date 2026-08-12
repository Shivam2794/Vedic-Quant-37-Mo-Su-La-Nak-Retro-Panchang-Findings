import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

SLIPPAGE_BPS = 10 / 10000

def run_return_stacked():
    print("[*] Downloading Return Stacked Universe...")
    offensive = ['SPY', 'EFA', 'EEM', 'AGG']
    defensive = ['LQD', 'IEF', 'SHY']
    beta = ['UPRO', 'TMF']
    cash = ['SHV']
    
    tickers = list(set(offensive + defensive + beta + cash))
    
    df = yf.download(tickers, start="2010-01-01", end="2024-01-01")['Close']
    df = df[~df.index.duplicated(keep='first')]
    df = df.ffill().dropna()
    
    returns = df.pct_change().dropna()
    
    # --- VAA Momentum Score ---
    p0 = df
    p1 = df.shift(21)
    p3 = df.shift(63)
    p6 = df.shift(126)
    p12 = df.shift(252)
    
    vaa_score = 12 * (p0 / p1 - 1) + 4 * (p0 / p3 - 1) + 2 * (p0 / p6 - 1) + 1 * (p0 / p12 - 1)
    
    df['YearMonth'] = df.index.to_period('M')
    month_ends = df.groupby('YearMonth').tail(1).index
    
    weights = pd.DataFrame(np.nan, index=df.index, columns=tickers)
    
    for date in month_ends:
        if date not in vaa_score.index or pd.isna(vaa_score.loc[date, 'SPY']):
            continue
            
        for col in tickers:
            weights.loc[date, col] = 0.0
            
        # 1. Beta Sleeve (60% allocation)
        # 30% UPRO, 30% TMF
        w_upro = 0.30
        w_tmf = 0.30
        
        # 2. Trend Sleeve (40% allocation to VAA)
        off_scores = vaa_score.loc[date, offensive]
        if isinstance(off_scores, pd.DataFrame): off_scores = off_scores.iloc[0]
            
        def_scores = vaa_score.loc[date, defensive]
        if isinstance(def_scores, pd.DataFrame): def_scores = def_scores.iloc[0]
            
        w_trend = {col: 0.0 for col in tickers}
        if (off_scores < 0).any(): 
            best_def = def_scores.idxmax()
            w_trend[best_def] = 0.40
        else:
            best_off = off_scores.idxmax()
            w_trend[best_off] = 0.40
            
        # Combine base weights
        weights.loc[date, 'UPRO'] += w_upro
        weights.loc[date, 'TMF'] += w_tmf
        for k, v in w_trend.items():
            weights.loc[date, k] += v

    weights = weights.ffill().shift(1).fillna(0.0)
    
    valid_idx = returns.index.intersection(weights.index)[252:]
    weights = weights.loc[valid_idx]
    r = returns.loc[valid_idx]
    
    # Calculate pre-vol-target returns
    raw_port_ret = (weights * r).sum(axis=1)
    
    # --- Overlay: Volatility Targeting (10% Target) ---
    # We apply vol targeting on a daily basis (or just dynamically scale exposure)
    # Using 20-day realized volatility of the raw portfolio
    vol20 = raw_port_ret.rolling(20).std() * np.sqrt(252)
    TARGET_VOL = 0.10
    
    vol_target_weights = pd.DataFrame(np.nan, index=weights.index, columns=tickers)
    
    for date in month_ends:
        if date not in vol20.index or pd.isna(vol20.loc[date]):
            continue
            
        current_vol = vol20.loc[date]
        if current_vol == 0:
            continue
            
        multiplier = TARGET_VOL / current_vol
        multiplier = min(multiplier, 1.5) # Allow 1.5x leverage on top if very low vol
        
        for col in tickers:
            vol_target_weights.loc[date, col] = weights.loc[date, col] * multiplier
            
        # The rest goes to Cash
        vol_target_weights.loc[date, 'SHV'] += (1.0 - multiplier)
        
    vol_target_weights = vol_target_weights.ffill().shift(1).fillna(0.0)
    
    final_idx = r.index.intersection(vol_target_weights.index)[20:]
    vol_target_weights = vol_target_weights.loc[final_idx]
    r = r.loc[final_idx]
    
    final_port_ret = (vol_target_weights * r).sum(axis=1)
    
    # Turnover calculation
    delta = pd.Series(0.0, index=vol_target_weights.index)
    rebalance_dates = [d for d in month_ends if d in vol_target_weights.index]
    for i in range(1, len(rebalance_dates)):
        curr = rebalance_dates[i]
        prev = rebalance_dates[i-1]
        delta.loc[curr] = (vol_target_weights.loc[curr] - vol_target_weights.loc[prev]).abs().sum()
        
    final_port_ret -= (delta * SLIPPAGE_BPS)
    
    cagr = (1 + final_port_ret).prod() ** (252 / len(final_port_ret)) - 1
    sharpe = np.sqrt(252) * final_port_ret.mean() / (final_port_ret.std() + 1e-9)
    
    cum_ret = (1 + final_port_ret).cumprod()
    max_dd = ((cum_ret - cum_ret.cummax()) / cum_ret.cummax()).min()
    annual_turnover = delta.sum() * 252 / len(final_port_ret)
    
    print("========================================================")
    print(f"[*] RETURN STACKED VOL-TARGETED RESULTS")
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
    run_return_stacked()
