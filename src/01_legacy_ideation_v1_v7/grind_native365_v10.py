"""
RELENTLESS GRINDER: V10 WITH NATIVE 365-DAY BTC TREND + FABLE IDEAS
Tests native 365-day BTC moving average + Fable Idea 8 (Tranching) + Idea 9 (Patience Dial).
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
    
    # Raw 365-day BTC series before ffill
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
    return close_p, btc_raw, biz_idx, valid_idx, r_mat, cy_arr, delta_days, assets

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

def test_native_365():
    close_p, btc_raw, biz_idx, valid_idx, r_mat, cy_arr, delta_days, assets = get_data()
    
    # Native 365-day BTC trend signals
    btc_trend_365 = (btc_raw.rolling(10).mean() > btc_raw.rolling(100).mean()).astype(float)
    btc_trend_biz = btc_trend_365.reindex(biz_idx).ffill().fillna(0.0)
    
    # BTC native 365 vol target
    btc_r_365 = btc_raw.pct_change()
    btc_vol_365 = btc_r_365.rolling(20).std() * np.sqrt(365)
    btc_vw_biz = (0.15 / btc_vol_365).clip(upper=1.5).reindex(biz_idx).ffill().shift(1).fillna(0.0)
    
    for b_w in [0.50, 0.55, 0.60, 0.65]:
        for g_w in [0.15, 0.20, 0.25]:
            s_w = round(1.0 - b_w - g_w, 2)
            if s_w < 0.10: continue
            
            w_df = pd.DataFrame(0.0, index=biz_idx, columns=assets)
            w_df['BTC-USD'] = btc_trend_biz * btc_vw_biz * b_w
            
            for t, w_val in [('GLD', g_w), ('SPY', s_w)]:
                c = close_p[t].ffill().reindex(biz_idx).ffill()
                vol20 = c.pct_change().rolling(20).std() * np.sqrt(252)
                vw = (0.15 / vol20).clip(upper=1.5).shift(1).fillna(0.0)
                trend = (c.rolling(10).mean() > c.rolling(100).mean()).astype(float)
                w_df[t] = trend * vw * w_val
                
            # Mode B evaluation
            cagr, sh, dd, _ = eval_w(w_df, valid_idx, r_mat, cy_arr, delta_days, lag=1)
            
            # Plus Idea 8 (K=2 Tranching)
            w_k2 = w_df.rolling(2).mean().fillna(w_df)
            cagr_k2, sh_k2, dd_k2, _ = eval_w(w_k2, valid_idx, r_mat, cy_arr, delta_days, lag=1)
            
            print(f"[%s/%s/%s] Native Mode B Raw:  Sharpe=%5.2f | MaxDD=%6.2f%% | CAGR=%6.2f%%" % (int(b_w*100), int(g_w*100), int(s_w*100), sh, dd*100, cagr*100))
            print(f"[%s/%s/%s] + Idea 8 Tranching: Sharpe=%5.2f | MaxDD=%6.2f%% | CAGR=%6.2f%%" % (int(b_w*100), int(g_w*100), int(s_w*100), sh_k2, dd_k2*100, cagr_k2*100))

if __name__ == "__main__":
    test_native_365()
