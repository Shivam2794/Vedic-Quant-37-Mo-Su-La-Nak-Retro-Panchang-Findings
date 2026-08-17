"""
EXHAUSTIVE GRIND ACROSS ALL 12 FABLE INSTITUTIONAL IDEAS
========================================================
Relentlessly evaluates standalone and smart combinations across all 12 modules
to identify high-Sharpe (>= 1.50) and low-DD (< 15%) institutional engines under Mode B 1-Bar Lag.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def get_data():
    assets = ['BTC-USD', 'GLD', 'SPY']
    tickers = assets + ['^IRX']
    df_raw = yf.download(tickers, start="2014-01-01", end="2024-01-01", progress=False, auto_adjust=False)
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
    return cagr, sharpe, dd, port_ret

def run_grind():
    close_p, biz_idx, valid_idx, r_mat, cy_arr, delta_days, assets = get_data()
    
    print("\n" + "="*90)
    print("RELENTLESS GRINDER: 12-IDEA SYSTEMATIC EVALUATION REPORT (MODE B 1-BAR LAG)")
    print("="*90)
    
    # 1. Base V9 Tri-Asset (10/100 trend, 15% Vol Target)
    w_base = pd.DataFrame(0.0, index=biz_idx, columns=assets)
    for idx_a, t in enumerate(assets):
        c = close_p[t].ffill().reindex(biz_idx).ffill()
        vol20 = c.pct_change().rolling(20).std() * np.sqrt(252)
        vw = (0.15 / vol20).clip(upper=1.5).shift(1).fillna(0.0)
        alloc = [0.50, 0.25, 0.25][idx_a]
        trend = (c.rolling(10).mean() > c.rolling(100).mean()).astype(float)
        w_base[t] = trend * vw * alloc
        
    cagr, sh, dd, _ = eval_w(w_base, valid_idx, r_mat, cy_arr, delta_days)
    print(f"%-50s | CAGR: %6.2f%% | Sharpe: %5.2f | MaxDD: %6.2f%%" % ("Baseline V9 Tri-Asset (50/25/25)", cagr*100, sh, dd*100))
    
    # Let's test combinations of:
    # - BTC Trend lookbacks (e.g. 10/100 vs 15/150 vs 20/200)
    # - Idea 8: Tranching (K=2)
    # - Idea 9: Patience Dial (tau=0.85)
    # - Idea 4: Drawdown Governor CPPI Floor
    # - Asset Weights
    
    best_candidate_name = None
    best_candidate_sharpe = 0.0
    best_candidate_w = None
    best_candidate_dd = 0.0
    best_candidate_cagr = 0.0
    
    for b_w in [0.50, 0.55, 0.60]:
        for g_w in [0.20, 0.25]:
            s_w = round(1.0 - b_w - g_w, 2)
            for fast_ma, slow_ma in [(10, 100), (15, 120), (20, 150)]:
                w_test = pd.DataFrame(0.0, index=biz_idx, columns=assets)
                for idx_a, t in enumerate(assets):
                    c = close_p[t].ffill().reindex(biz_idx).ffill()
                    vol20 = c.pct_change().rolling(20).std() * np.sqrt(252)
                    vw = (0.15 / vol20).clip(upper=1.5).shift(1).fillna(0.0)
                    alloc = [b_w, g_w, s_w][idx_a]
                    trend = (c.rolling(fast_ma).mean() > c.rolling(slow_ma).mean()).astype(float)
                    w_test[t] = trend * vw * alloc
                
                # Apply Idea 8 (K=2 Tranching) + Idea 9 (tau=0.85 Patience Dial)
                w_mod = w_test.rolling(2).mean().fillna(w_test).ewm(alpha=0.85).mean()
                cagr_i, sh_i, dd_i, _ = eval_w(w_mod, valid_idx, r_mat, cy_arr, delta_days)
                
                if sh_i > best_candidate_sharpe:
                    best_candidate_sharpe = sh_i
                    best_candidate_dd = dd_i
                    best_candidate_cagr = cagr_i
                    best_candidate_name = f"V10 Apex Idea 8+9 [{int(b_w*100)}/{int(g_w*100)}/{int(s_w*100)}] MA({fast_ma}/{slow_ma})"
                    best_candidate_w = w_mod
                    
    print(f"%-50s | CAGR: %6.2f%% | Sharpe: %5.2f | MaxDD: %6.2f%%" % (best_candidate_name, best_candidate_cagr*100, best_candidate_sharpe, best_candidate_dd*100))
    print("="*90)
    
    # Save best weights to disk for 3x Brutal Multipoint Quality Inspection
    best_candidate_w.to_csv("best_v10_candidate_weights.csv")
    print(f"[+] Saved {best_candidate_name} weights to best_v10_candidate_weights.csv")

if __name__ == "__main__":
    run_grind()
