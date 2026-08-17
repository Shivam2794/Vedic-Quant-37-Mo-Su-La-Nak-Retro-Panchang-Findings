import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def run_path3():
    print("[*] PATH 3: Multi-Asset Institutional Macro Portfolio...")
    assets = ['SPY', 'QQQ', 'TLT', 'GLD', 'BTC-USD', 'UUP', 'LQD']
    tickers = assets + ['^IRX']
    df_raw = yf.download(tickers, start="2014-01-01", end="2024-01-01", progress=False, auto_adjust=False)
    
    biz_idx = df_raw['Close']['SPY'].dropna().index
    df_raw = df_raw.ffill()
    
    close_prices = df_raw['Close']
    open_prices = df_raw['Open']
    irx = df_raw['Close']['^IRX']
    
    valid_idx = biz_idx[250:-1]
    delta_days = biz_idx.to_series().diff().shift(-1).dt.days.loc[valid_idx].fillna(1).values
    
    open_biz = open_prices.ffill().reindex(biz_idx).ffill()
    r_open = (open_biz.shift(-1) / open_biz) - 1
    r_mat = r_open[assets].loc[valid_idx].values
    
    irx = irx.ffill().reindex(biz_idx).ffill().shift(1)
    cy = (irx / 100) / 252
    cy = cy.fillna(0.0001)
    cy_arr = cy.loc[valid_idx].values
    
    slip_cost = np.array([0.0003, 0.0003, 0.0003, 0.0003, 0.0020, 0.0003, 0.0003])
    num_assets = len(assets)
    base_w = 1.0 / num_assets
    
    fast, slow, vt = 10, 150, 0.15
    master_weights = pd.DataFrame(0.0, index=biz_idx, columns=assets)
    
    for t in assets:
        c = close_prices[t]
        if t == 'BTC-USD':
            sma_fast = c.rolling(fast).mean()
            sma_slow = c.rolling(slow).mean()
            trend = (sma_fast > sma_slow).astype(float).shift(1).fillna(0.0)
            vol20 = c.pct_change().rolling(20).std() * np.sqrt(365)
            vol_w = (vt / vol20).clip(upper=1.5).shift(1).fillna(0.0)
            target_weights_365 = trend * vol_w
            master_weights[t] = target_weights_365.ffill().reindex(biz_idx).ffill() * base_w
        else:
            c_biz = c.ffill().reindex(biz_idx).ffill()
            sma_fast = c_biz.rolling(fast).mean()
            sma_slow = c_biz.rolling(slow).mean()
            trend = (sma_fast > sma_slow).astype(float).shift(1).fillna(0.0)
            vol20 = c_biz.pct_change().rolling(20).std() * np.sqrt(252)
            vol_w = (vt / vol20).clip(upper=1.5).shift(1).fillna(0.0)
            master_weights[t] = trend * vol_w * base_w
            
    target_w = master_weights.loc[valid_idx].values
    final_port_ret = np.zeros(len(valid_idx))
    prev_actual_w = np.zeros(num_assets)
    
    for i in range(len(valid_idx)):
        w = target_w[i]
        turnover = np.abs(w - prev_actual_w)
        slip = np.sum(turnover * slip_cost)
        cash = 1.0 - np.sum(np.abs(w))
        a_ret = np.sum(w * r_mat[i])
        
        if cash > 0:
            c_ret = cash * cy_arr[i] * delta_days[i]
        else:
            c_ret = cash * (cy_arr[i] + (0.015 / 252)) * delta_days[i]
            
        port_ret = a_ret + c_ret - slip
        final_port_ret[i] = port_ret
        
        if port_ret > -1.0:
            drift_factor = (1.0 + r_mat[i]) / (1.0 + port_ret)
            prev_actual_w = w * drift_factor
        else:
            prev_actual_w = np.zeros(num_assets)
            
    excess = final_port_ret - (cy_arr * delta_days)
    std = np.std(final_port_ret, ddof=1)
    sharpe = np.sqrt(252) * np.mean(excess) / std
    cagr = np.prod(1 + final_port_ret) ** (252 / len(final_port_ret)) - 1
    cum = np.cumprod(1 + final_port_ret)
    cummax = np.maximum.accumulate(cum)
    max_dd = np.min((cum - cummax) / cummax)
    
    print("=" * 55)
    print(f"[PATH 3: MULTI-ASSET MACRO PORTFOLIO (7 ASSETS)]")
    print(f"  CAGR:   {cagr:.2%}")
    print(f"  Sharpe: {sharpe:.2f}")
    print(f"  Max DD: {max_dd:.2%}")
    print("=" * 55)

if __name__ == "__main__":
    run_path3()
