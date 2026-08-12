"""
RELENTLESS GRINDER: 12-IDEA STANDALONE & COMBINATION GRID
Tests each of Fable's 12 Institutional Creative Genius Quant Ideas individually
and in smart combinations under Mode B (Hard 1-Bar Execution Lag).
"""

import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def get_data():
    assets = ['BTC-USD', 'GLD', 'SPY']
    tickers = assets + ['^IRX']
    df_raw = yf.download(tickers, start="2014-01-01", end="2024-01-01", progress=False)
    biz_idx = df_raw['Close']['SPY'].dropna().index
    df_raw = df_raw.ffill()
    close_p = df_raw['Close']
    open_p = df_raw['Open']
    irx = df_raw['Close']['^IRX']
    valid_idx = biz_idx[250:-1]
    delta_days = biz_idx.to_series().diff().shift(-1).dt.days.loc[valid_idx].fillna(1).values
    open_biz = open_p.ffill().reindex(biz_idx).ffill()
    r_open = (open_biz.shift(-1) / open_biz) - 1
    r_mat = r_open[assets].loc[valid_idx].values
    irx_biz = irx.ffill().reindex(biz_idx).ffill().shift(1)
    cy = (irx_biz / 100) / 252
    cy_arr = cy.fillna(0.0001).loc[valid_idx].values
    return close_p, biz_idx, valid_idx, r_mat, cy_arr, delta_days, assets

def eval_w(weights_matrix, valid_idx, r_mat, cy_arr, delta_days, lag=1):
    w_target = weights_matrix.shift(lag).loc[valid_idx].fillna(0.0).values
    slip_cost = np.array([0.0020, 0.0003, 0.0003])
    n = len(valid_idx)
    port_ret = np.zeros(n)
    prev_w = np.zeros(3)
    for i in range(n):
        w = w_target[i]
        turnover = np.abs(w - prev_w)
        slip = np.sum(turnover * slip_cost)
        cash = 1.0 - np.sum(np.abs(w))
        a_ret = np.sum(w * r_mat[i])
        if cash > 0:
            c_ret = cash * cy_arr[i] * delta_days[i]
        else:
            c_ret = cash * (cy_arr[i] + (0.015 / 252)) * delta_days[i]
        ret = a_ret + c_ret - slip
        port_ret[i] = ret
        if ret > -1.0:
            prev_w = w * ((1.0 + r_mat[i]) / (1.0 + ret))
        else:
            prev_w = np.zeros_like(w)
    excess = port_ret - (cy_arr * delta_days)
    std = np.std(port_ret, ddof=1)
    sharpe = np.sqrt(252) * np.mean(excess) / std
    cagr = np.prod(1 + port_ret) ** (252 / n) - 1
    cum = np.cumprod(1 + port_ret)
    cummax = np.maximum.accumulate(cum)
    dd = np.min((cum - cummax) / cummax)
    return cagr, sharpe, dd

def run_grid():
    close_p, biz_idx, valid_idx, r_mat, cy_arr, delta_days, assets = get_data()
    
    # Base V9 Tri-Asset
    w_base = pd.DataFrame(0.0, index=biz_idx, columns=assets)
    for idx_a, t in enumerate(assets):
        c = close_p[t].ffill().reindex(biz_idx).ffill()
        vol20 = c.pct_change().rolling(20).std() * np.sqrt(252)
        vw = (0.15 / vol20).clip(upper=1.5).shift(1).fillna(0.0)
        alloc = [0.50, 0.25, 0.25][idx_a]
        trend = (c.rolling(10).mean() > c.rolling(100).mean()).astype(float)
        w_base[t] = trend * vw * alloc
        
    print(f"[*] Base V9 Tri-Asset Mode B: {eval_w(w_base, valid_idx, r_mat, cy_arr, delta_days)}")
    
    # Idea 4: Drawdown Governor CPPI Floor (Ratcheting HWM Floor at 88%)
    # Let's test CPPI Drawdown Governor overlay
    # Idea 9: Patience Dial Gârleanu-Pedersen Partial Adjustment tau
    taus = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    best_tau_sharpe = 0
    best_tau = 1.0
    for tau in taus:
        w_gp = w_base.ewm(alpha=tau).mean()
        cagr, sh, dd = eval_w(w_gp, valid_idx, r_mat, cy_arr, delta_days)
        if sh > best_tau_sharpe:
            best_tau_sharpe = sh
            best_tau = tau
    print(f"[*] Idea 9 Patience Dial (tau={best_tau}): Sharpe={best_tau_sharpe:.3f}")
    
    # Idea 8: Tranching Engine K=2, 3, 5
    for k in [2, 3, 5]:
        w_k = w_base.rolling(k).mean().fillna(w_base)
        cagr, sh, dd = eval_w(w_k, valid_idx, r_mat, cy_arr, delta_days)
        print(f"[*] Idea 8 Tranching (K={k}): Sharpe={sh:.3f}, MaxDD={dd*100:.2f}%")
        
    # Let's test allocating [0.55 BTC, 0.25 GLD, 0.20 SPY] with Idea 9 Patience Dial
    for b_w in [0.45, 0.50, 0.55, 0.60]:
        for g_w in [0.20, 0.25, 0.30]:
            s_w = round(1.0 - b_w - g_w, 2)
            if s_w < 0.10: continue
            w_test = pd.DataFrame(0.0, index=biz_idx, columns=assets)
            for idx_a, t in enumerate(assets):
                c = close_p[t].ffill().reindex(biz_idx).ffill()
                vol20 = c.pct_change().rolling(20).std() * np.sqrt(252)
                vw = (0.15 / vol20).clip(upper=1.5).shift(1).fillna(0.0)
                alloc = [b_w, g_w, s_w][idx_a]
                trend = (c.rolling(10).mean() > c.rolling(100).mean()).astype(float)
                w_test[t] = trend * vw * alloc
            
            w_test_gp = w_test.ewm(alpha=0.5).mean()
            cagr, sh, dd = eval_w(w_test_gp, valid_idx, r_mat, cy_arr, delta_days)
            if sh >= 1.48:
                print(f"  -> Allocation [{b_w} BTC, {g_w} GLD, {s_w} SPY] + Idea 9 (tau=0.5): Sharpe={sh:.3f}, MaxDD={dd*100:.2f}%, CAGR={cagr*100:.2f}%")

if __name__ == "__main__":
    run_grid()
