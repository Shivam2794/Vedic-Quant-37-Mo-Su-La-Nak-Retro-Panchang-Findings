"""
OMNI-ALLOCATOR IDEA 5: VOL-OF-VOL BRAKE
Implements the Tri-Asset (60/20/20) institutional core with Fable Idea 5:
A Vol-of-Vol Brake that scales down BTC exposure when its 60-day Vol-of-Vol exceeds the 90th percentile.
Executes under exact Mode B (1-bar institutional lag).
"""

import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def run_idea5():
    assets = ['BTC-USD', 'GLD', 'SPY']
    tickers = assets + ['^IRX']
    df_raw = yf.download(tickers, start="2014-01-01", end="2024-01-01", progress=False, auto_adjust=False)
    
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
    cy = (irx_biz / 100) / 365
    cy_arr = cy.fillna(0.0001).loc[valid_idx].values
    
    # --------------------------------------------------------------------------
    # SIGNAL LAYER (MODE B: Shifted exactly 1 bar so trade fills at Open t+1)
    # --------------------------------------------------------------------------
    btc_trend = (btc_raw.rolling(2).mean() > btc_raw.rolling(40).mean()).astype(float).shift(1).fillna(0.0)
    btc_vol = btc_raw.pct_change().rolling(20).std() * np.sqrt(365)
    btc_vw = (0.15 / btc_vol).clip(upper=1.5).shift(1).fillna(0.0)
    
    # IDEA 5: Volatility-of-Volatility Brake
    btc_vov = btc_vol.rolling(60).std()
    vov_brake = (btc_vov < btc_vov.rolling(365).quantile(0.90).fillna(np.inf)).astype(float).shift(1)
    vov_brake_biz = vov_brake.reindex(biz_idx).ffill().fillna(1.0)
    
    btc_w = (btc_trend * btc_vw).reindex(biz_idx).ffill().fillna(0.0) * 0.60
    # Apply Brake
    btc_w = btc_w * vov_brake_biz
    
    gld_c = close_p['GLD'].ffill().reindex(biz_idx).ffill()
    gld_vw = (0.15 / (gld_c.pct_change().rolling(20).std() * np.sqrt(252))).clip(upper=1.5).shift(1).fillna(0.0)
    gld_trend = (gld_c.rolling(10).mean() > gld_c.rolling(100).mean()).astype(float).shift(1).fillna(0.0)
    gld_w = (gld_trend * gld_vw) * 0.20
    
    spy_c = close_p['SPY'].ffill().reindex(biz_idx).ffill()
    spy_vw = (0.15 / (spy_c.pct_change().rolling(20).std() * np.sqrt(252))).clip(upper=1.5).shift(1).fillna(0.0)
    spy_trend = (spy_c.rolling(10).mean() > spy_c.rolling(100).mean()).astype(float).shift(1).fillna(0.0)
    spy_w = (spy_trend * spy_vw) * 0.20
    
    w_df = pd.DataFrame({'BTC-USD': btc_w, 'GLD': gld_w, 'SPY': spy_w}, index=biz_idx)
    w_target = w_df.loc[valid_idx].fillna(0.0).values
    
    # --------------------------------------------------------------------------
    # EXECUTION
    # --------------------------------------------------------------------------
    slip_cost = np.array([0.0020, 0.0003, 0.0003])
    n = len(valid_idx)
    port_ret = np.zeros(n)
    prev_w = np.zeros(3)
    
    for i in range(n):
        w_exec = w_target[i]
        turnover = np.abs(w_exec - prev_w)
        slip = np.sum(turnover * slip_cost)
        cash = 1.0 - np.sum(np.abs(w_exec))
        a_ret = np.sum(w_exec * r_mat[i])
        
        if cash > 0:
            c_ret = cash * cy_arr[i] * delta_days[i]
        else:
            c_ret = cash * (cy_arr[i] + (0.015 / 365)) * delta_days[i]
            
        ret = a_ret + c_ret - slip
        port_ret[i] = ret
        
        if ret > -1.0:
            prev_w = w_exec * ((1.0 + r_mat[i]) / (1.0 + ret))
        else:
            prev_w = np.zeros_like(w_exec)
            
    excess = port_ret - (cy_arr * delta_days)
    std = np.std(port_ret, ddof=1)
    sharpe = np.sqrt(252) * np.mean(excess) / std
    cagr = np.prod(1 + port_ret) ** (252 / n) - 1
    cum = np.cumprod(1 + port_ret)
    cummax = np.maximum.accumulate(cum)
    dd = np.min((cum - cummax) / cummax)
    
    print("\n" + "="*80)
    print("IDEA 5: VOL-OF-VOL BRAKE PERFORMANCE (MODE B 1-BAR LAG)")
    print("="*80)
    print(f"CAGR   : {cagr*100:6.2f}%")
    print(f"Sharpe : {sharpe:6.2f}")
    print(f"MaxDD  : {dd*100:6.2f}%")
    print("="*80)
    
    return cagr, sharpe, dd

if __name__ == "__main__":
    run_idea5()
