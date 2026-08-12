"""
RELENTLESS GRINDER: EXACT MODE B EXECUTION LAG CHECK
Verifies that we apply exactly 1-bar execution lag (Friday Close signal -> Monday Open trade),
and tests our institutional tri-asset combinations with Fable Idea 8 (Tranching) & Idea 9 (Patience Dial).
"""

import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def run_exact_mode_b():
    assets = ['BTC-USD', 'GLD', 'SPY']
    tickers = assets + ['^IRX']
    df_raw = yf.download(tickers, start="2014-01-01", end="2024-01-01", progress=False)
    
    biz_idx = df_raw['Close']['SPY'].dropna().index
    btc_raw = df_raw['Close']['BTC-USD'].dropna()
    
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
    
    # EXACT 1-BAR MODE B LAG:
    # Compute signals on close at time t, then shift(1) so they execute at open t+1.
    
    # 1. BTC Native 365 (2/40 and 10/100)
    btc_trend_2_40 = (btc_raw.rolling(2).mean() > btc_raw.rolling(40).mean()).astype(float).shift(1).fillna(0.0)
    btc_trend_10_100 = (btc_raw.rolling(10).mean() > btc_raw.rolling(100).mean()).astype(float).shift(1).fillna(0.0)
    
    btc_vol = btc_raw.pct_change().rolling(20).std() * np.sqrt(365)
    btc_vw = (0.15 / btc_vol).clip(upper=1.5).shift(1).fillna(0.0)
    
    btc_w_2_40 = (btc_trend_2_40 * btc_vw).reindex(biz_idx).ffill().fillna(0.0)
    btc_w_10_100 = (btc_trend_10_100 * btc_vw).reindex(biz_idx).ffill().fillna(0.0)
    
    # GLD & SPY Signals (10/100) shifted 1 bar
    gld_c = close_p['GLD'].ffill().reindex(biz_idx).ffill()
    gld_vw = (0.15 / (gld_c.pct_change().rolling(20).std() * np.sqrt(252))).clip(upper=1.5).shift(1).fillna(0.0)
    gld_trend = (gld_c.rolling(10).mean() > gld_c.rolling(100).mean()).astype(float).shift(1).fillna(0.0)
    gld_w = gld_trend * gld_vw
    
    spy_c = close_p['SPY'].ffill().reindex(biz_idx).ffill()
    spy_vw = (0.15 / (spy_c.pct_change().rolling(20).std() * np.sqrt(252))).clip(upper=1.5).shift(1).fillna(0.0)
    spy_trend = (spy_c.rolling(10).mean() > spy_c.rolling(100).mean()).astype(float).shift(1).fillna(0.0)
    spy_w = spy_trend * spy_vw
    
    def eval_weights(w_df):
        w_target = w_df.loc[valid_idx].fillna(0.0).values
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
        
    print("\n" + "="*80)
    print("EXACT 1-BAR MODE B EVALUATION (NO DOUBLE SHIFT)")
    print("="*80)
    
    # 1. Pure BTC V8 Benchmark (2/40)
    w_btc_only = pd.DataFrame({'BTC-USD': btc_w_2_40, 'GLD': 0.0, 'SPY': 0.0}, index=biz_idx)
    cagr, sh, dd = eval_weights(w_btc_only)
    print(f"%-50s | CAGR: %6.2f%% | Sharpe: %5.2f | MaxDD: %6.2f%%" % ("V8 Benchmark BTC Only (SMA 2/40)", cagr*100, sh, dd*100))
    
    # 2. Pure BTC 10/100 Benchmark
    w_btc_100 = pd.DataFrame({'BTC-USD': btc_w_10_100, 'GLD': 0.0, 'SPY': 0.0}, index=biz_idx)
    cagr, sh, dd = eval_weights(w_btc_100)
    print(f"%-50s | CAGR: %6.2f%% | Sharpe: %5.2f | MaxDD: %6.2f%%" % ("BTC Only (SMA 10/100)", cagr*100, sh, dd*100))
    
    # 3. Tri-Asset Portfolio [60% BTC (2/40), 20% GLD, 20% SPY] + Fable Idea 8 Tranching + Idea 9 Patience Dial
    for b_alloc in [0.60, 0.65, 0.70]:
        rem = round(1.0 - b_alloc, 2)
        g_alloc = round(rem / 2, 2)
        s_alloc = round(rem - g_alloc, 2)
        w_tri = pd.DataFrame({
            'BTC-USD': btc_w_2_40 * b_alloc,
            'GLD': gld_w * g_alloc,
            'SPY': spy_w * s_alloc
        }, index=biz_idx)
        
        cagr, sh, dd = eval_weights(w_tri)
        
        # Fable Idea 8 (Tranching K=2) + Idea 9 (Patience Dial tau=0.85)
        w_fable = w_tri.rolling(2).mean().fillna(w_tri).ewm(alpha=0.85).mean()
        cagr_f, sh_f, dd_f = eval_weights(w_fable)
        
        print(f"Tri-Asset [%2d/%2d/%2d] Raw Mode B                    | CAGR: %6.2f%% | Sharpe: %5.2f | MaxDD: %6.2f%%" % (int(b_alloc*100), int(g_alloc*100), int(s_alloc*100), cagr*100, sh, dd*100))
        print(f"Tri-Asset [%2d/%2d/%2d] + Fable Idea 8 & 9 (Apex)      | CAGR: %6.2f%% | Sharpe: %5.2f | MaxDD: %6.2f%%" % (int(b_alloc*100), int(g_alloc*100), int(s_alloc*100), cagr_f*100, sh_f, dd_f*100))
        print("-" * 80)

if __name__ == "__main__":
    run_exact_mode_b()
