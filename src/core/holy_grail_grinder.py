import yfinance as yf
import pandas as pd
import numpy as np
import itertools
import warnings
import json
warnings.filterwarnings('ignore')

# ---------------------------------------------------------
# 1. DATA INGESTION 
# ---------------------------------------------------------
def get_traditional_data():
    tickers = ['SPY', 'QQQ', 'GLD', 'TLT', 'UPRO', 'TMF', 'SHY', 'BIL']
    df_raw = yf.download(tickers, start="2005-01-01", end="2024-01-01", progress=False, auto_adjust=False)
    df_raw = df_raw.ffill()
    close_p = df_raw['Close'].dropna()
    returns = close_p.pct_change().dropna()
    
    if 'UPRO' not in returns.columns or returns['UPRO'].isnull().all():
        returns['UPRO'] = returns['SPY'] * 3.0 - (0.01 / 252)
    if 'TMF' not in returns.columns or returns['TMF'].isnull().all():
        returns['TMF'] = returns['TLT'] * 3.0 - (0.01 / 252)
        
    for col in ['UPRO', 'TMF']:
        if col in close_p.columns:
            simulated_ret = returns['SPY'] * 3.0 - (0.01 / 252) if col == 'UPRO' else returns['TLT'] * 3.0 - (0.01 / 252)
            mask = returns[col].isnull() | (returns[col] == 0.0)
            returns.loc[mask, col] = simulated_ret[mask]

    return returns, close_p.loc[returns.index]

# ---------------------------------------------------------
# 2. METRICS (STRICT 1-BAR LAG & 20bps ROUNDTRIP)
# ---------------------------------------------------------
def calculate_metrics(r_mat, w_mat):
    w_exec = np.roll(w_mat, 1, axis=0)
    w_exec[0] = 0.0
    
    N = len(r_mat)
    port_ret = np.zeros(N)
    slip_cost = 0.0010 
    
    for i in range(1, N):
        prev_w = w_exec[i-1]
        curr_w = w_exec[i]
        
        turnover = np.sum(np.abs(curr_w - prev_w))
        slip = turnover * slip_cost
        cash_w = max(0, 1.0 - np.sum(np.abs(curr_w)))
        
        ret = np.sum(curr_w * r_mat[i]) + cash_w * 0.0 - slip
        port_ret[i] = ret
        
    std = np.std(port_ret, ddof=1)
    sharpe = np.sqrt(252) * np.mean(port_ret) / std if std > 0 else 0.0
    cagr = np.prod(1.0 + port_ret)**(252/N) - 1.0
    cum = np.cumprod(1.0 + port_ret)
    peak = np.maximum.accumulate(cum)
    dd = (cum - peak) / peak
    max_dd = np.min(dd)
    
    return sharpe, cagr, max_dd

# ---------------------------------------------------------
# 3. GENIUS GRINDER ENGINE
# ---------------------------------------------------------
# Test combinations of:
# Base Allocation: [SPY/TLT, QQQ/TLT, UPRO/TMF]
# Weights: [60/40, 55/45, 40/60]
# Trend Filter (Asset goes to cash if below MA): [None, 100, 200, 250]
# Volatility Brake (Target Vol threshold for cash): [None, 0.15, 0.18, 0.20, 0.25]
# CPPI Floor: [None, 0.85, 0.90]

def simulate(close_p, returns, alloc_pair, weight_1, trend_ma, vol_thresh, cppi_floor):
    N = len(close_p)
    w_out = np.zeros((N, len(returns.columns)))
    
    idx_1 = returns.columns.get_loc(alloc_pair[0])
    idx_2 = returns.columns.get_loc(alloc_pair[1])
    shy_idx = returns.columns.get_loc('SHY')
    
    base_w1 = weight_1
    base_w2 = 1.0 - weight_1
    
    sma_1 = close_p[alloc_pair[0]].rolling(trend_ma).mean() if trend_ma else None
    sma_2 = close_p[alloc_pair[1]].rolling(trend_ma).mean() if trend_ma else None
    
    vol_1 = returns[alloc_pair[0]].rolling(20).std() * np.sqrt(252) if vol_thresh else None
    vol_2 = returns[alloc_pair[1]].rolling(20).std() * np.sqrt(252) if vol_thresh else None
    
    for i in range(max(20, trend_ma if trend_ma else 20), N):
        w1 = base_w1
        w2 = base_w2
        
        if trend_ma:
            if close_p[alloc_pair[0]].iloc[i] < sma_1.iloc[i]: w1 = 0.0
            if close_p[alloc_pair[1]].iloc[i] < sma_2.iloc[i]: w2 = 0.0
            
        if vol_thresh:
            if vol_1 is not None and vol_1.iloc[i] > vol_thresh: w1 = 0.0
            if vol_2 is not None and vol_2.iloc[i] > vol_thresh: w2 = 0.0
            
        cash_w = (base_w1 - w1) + (base_w2 - w2)
        
        w_out[i, idx_1] = w1
        w_out[i, idx_2] = w2
        w_out[i, shy_idx] = cash_w

    if cppi_floor is not None:
        # We must apply CPPI dynamically. Since CPPI requires knowing the actual portfolio return path,
        # we do a simulated path constraint
        nav = 1.0
        peak = 1.0
        w_exec = np.roll(w_out, 1, axis=0)
        w_exec[0] = 0.0
        w_cppi = np.zeros_like(w_out)
        r_mat = returns.values
        
        for i in range(1, N):
            curr_w = w_exec[i]
            cash_w = max(0, 1.0 - np.sum(np.abs(curr_w)))
            ret = np.sum(curr_w * r_mat[i]) + cash_w * 0.0 
            nav = nav * (1.0 + ret)
            if nav > peak: peak = nav
            floor = peak * cppi_floor
            cushion = max(0, (nav - floor) / nav)
            multiplier = 1.0 / (1.0 - cppi_floor) # E.g. floor 0.85 -> cushion 0.15 -> mult 6.66
            exposure = min(1.0, cushion * multiplier)
            w_cppi[i] = w_out[i] * exposure
            w_exec[i] = w_cppi[i] # Update execution path
        w_out = w_cppi
        
    return calculate_metrics(returns.values, w_out)

def grid_search():
    returns, close_p = get_traditional_data()
    
    pairs = [('SPY', 'TLT'), ('QQQ', 'TLT'), ('UPRO', 'TMF')]
    weights = [0.40, 0.50, 0.55, 0.60, 0.70]
    trend_mas = [None, 100, 200, 250]
    vol_threshs = [None, 0.15, 0.18, 0.20, 0.25]
    cppi_floors = [None, 0.80, 0.85, 0.90]
    
    results = []
    
    total = len(pairs) * len(weights) * len(trend_mas) * len(vol_threshs) * len(cppi_floors)
    print(f"Grinding {total} physical-reality combinations...")
    
    for p, w, t, v, c in itertools.product(pairs, weights, trend_mas, vol_threshs, cppi_floors):
        sr, cagr, dd = simulate(close_p, returns, p, w, t, v, c)
        if dd > -0.20 and sr > 0.8:
            results.append({
                'pair': p, 'w1': w, 'trend': t, 'vol': v, 'cppi': c,
                'sr': sr, 'cagr': cagr, 'dd': dd
            })
            
    results.sort(key=lambda x: x['sr'], reverse=True)
    print("\n--- TOP 10 MODELS (DD < 20%) ---")
    for r in results[:10]:
        print(f"SR: {r['sr']:.3f} | CAGR: {r['cagr']*100:.2f}% | DD: {r['dd']*100:.2f}% | Config: {r['pair']}, W={r['w1']}, SMA={r['trend']}, Vol={r['vol']}, CPPI={r['cppi']}")

    with open('top_no_btc_models.json', 'w') as f:
        json.dump(results[:10], f, indent=4)

if __name__ == "__main__":
    grid_search()
