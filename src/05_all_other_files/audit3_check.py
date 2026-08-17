import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def run_both():
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
    cy_arr = (irx_biz / 100) / 365
    cy_arr = cy_arr.fillna(0.0).loc[valid_idx].values
    
    btc_trend = (btc_raw.rolling(2).mean() > btc_raw.rolling(40).mean()).astype(float).shift(1).fillna(0.0)
    btc_vol = btc_raw.pct_change().rolling(20).std() * np.sqrt(365)
    btc_vw = (0.15 / btc_vol).clip(upper=1.5).shift(1).fillna(0.0)
    btc_w = (btc_trend * btc_vw).reindex(biz_idx).ffill().fillna(0.0) * 0.60
    
    gld_c = close_p['GLD'].ffill().reindex(biz_idx).ffill()
    gld_vw = (0.15 / (gld_c.pct_change().rolling(20).std() * np.sqrt(252))).clip(upper=1.5).shift(1).fillna(0.0)
    gld_trend = (gld_c.rolling(10).mean() > gld_c.rolling(100).mean()).astype(float).shift(1).fillna(0.0)
    gld_w = (gld_trend * gld_vw) * 0.20
    
    spy_c = close_p['SPY'].ffill().reindex(biz_idx).ffill()
    spy_vw = (0.15 / (spy_c.pct_change().rolling(20).std() * np.sqrt(252))).clip(upper=1.5).shift(1).fillna(0.0)
    spy_trend = (spy_c.rolling(10).mean() > spy_c.rolling(100).mean()).astype(float).shift(1).fillna(0.0)
    spy_w = (spy_trend * spy_vw) * 0.20
    
    w_df = pd.DataFrame({'BTC-USD': btc_w, 'GLD': gld_w, 'SPY': spy_w}, index=biz_idx)
    w_idea9_smooth = w_df.ewm(alpha=0.15, adjust=False).mean()
    
    w_target_raw = w_df.loc[valid_idx].fillna(0.0).values
    w_target_smooth = w_idea9_smooth.loc[valid_idx].fillna(0.0).values
    
    slip_cost = np.array([0.0020, 0.0003, 0.0003])
    n = len(valid_idx)
    
    # Run Unsmoothed
    prev_w = np.zeros(3)
    total_slip_raw = 0.0
    total_turnover_raw = 0.0
    for i in range(n):
        w_exec = w_target_raw[i]
        turnover = np.abs(w_exec - prev_w)
        total_turnover_raw += np.sum(turnover)
        slip = np.sum(turnover * slip_cost)
        total_slip_raw += slip
        cash = 1.0 - np.sum(np.abs(w_exec))
        a_ret = np.sum(w_exec * r_mat[i])
        c_ret = cash * cy_arr[i] * delta_days[i] if cash > 0 else cash * (cy_arr[i] + (0.015 / 252)) * delta_days[i]
        ret = a_ret + c_ret - slip
        if ret > -1.0:
            prev_w = w_exec * ((1.0 + r_mat[i]) / (1.0 + ret))
        else:
            prev_w = np.zeros_like(w_exec)
            
    # Run Smoothed
    prev_w = np.zeros(3)
    total_slip_smooth = 0.0
    total_turnover_smooth = 0.0
    for i in range(n):
        w_exec = w_target_smooth[i]
        turnover = np.abs(w_exec - prev_w)
        total_turnover_smooth += np.sum(turnover)
        slip = np.sum(turnover * slip_cost)
        total_slip_smooth += slip
        cash = 1.0 - np.sum(np.abs(w_exec))
        a_ret = np.sum(w_exec * r_mat[i])
        c_ret = cash * cy_arr[i] * delta_days[i] if cash > 0 else cash * (cy_arr[i] + (0.015 / 252)) * delta_days[i]
        ret = a_ret + c_ret - slip
        if ret > -1.0:
            prev_w = w_exec * ((1.0 + r_mat[i]) / (1.0 + ret))
        else:
            prev_w = np.zeros_like(w_exec)

    print(f"Raw Turnover: {total_turnover_raw:.2f}, Raw Slip Cost: {total_slip_raw*100:.2f}%")
    print(f"Smoothed Turnover: {total_turnover_smooth:.2f}, Smoothed Slip Cost: {total_slip_smooth*100:.2f}%")

if __name__ == "__main__":
    run_both()
