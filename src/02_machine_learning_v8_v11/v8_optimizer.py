import yfinance as yf
import pandas as pd
import numpy as np
from itertools import product
import warnings
warnings.filterwarnings('ignore')

def run_v8_optimizer():
    print(f"[*] Downloading Data for V8 Multi-Asset Optimizer...")
    assets = ['SPY', 'QQQ', 'TLT', 'GLD', 'BTC-USD', 'UUP', 'LQD']
    tickers = assets + ['^IRX']
    df_raw = yf.download(tickers, start="2014-01-01", end="2024-01-01", progress=False, auto_adjust=False)
    df_raw = df_raw.ffill()
    
    close_prices = df_raw['Close']
    open_prices = df_raw['Open']
    spy_close = df_raw['Close']['SPY'].dropna()
    irx = df_raw['Close']['^IRX']
    
    btc_close = close_prices['BTC-USD']
    biz_idx = spy_close.index
    open_biz = open_prices.ffill().reindex(biz_idx).ffill()
    r_open = (open_biz.shift(-1) / open_biz) - 1
    
    irx = irx.ffill().reindex(biz_idx).ffill().shift(1)
    cy = (irx / 100) / 252
    cy = cy.fillna(0.0001)
    
    valid_idx = biz_idx[250:-1]
    r_mat = r_open[assets].loc[valid_idx].values
    cy_arr = cy.loc[valid_idx].values
    
    slip_cost = np.array([0.0003, 0.0003, 0.0003, 0.0003, 0.0020, 0.0003, 0.0003])
    num_assets = len(assets)
    base_w = 1.0 / num_assets
    
    fast_mas = [10, 20, 50]
    slow_mas = [100, 150, 200]
    vol_targets = [0.05, 0.10, 0.15]
    
    best_sharpe = 0
    best_params = None
    
    for fast, slow, vt in product(fast_mas, slow_mas, vol_targets):
        
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
                c_ret = cash * cy_arr[i]
            else:
                c_ret = cash * (cy_arr[i] + (0.015 / 252))
                
            port_ret = a_ret + c_ret - slip
            final_port_ret[i] = port_ret
            
            if port_ret > -1.0:
                drift_factor = (1.0 + r_mat[i]) / (1.0 + port_ret)
                prev_actual_w = w * drift_factor
            else:
                prev_actual_w = np.zeros(num_assets)
                
        excess = final_port_ret - cy_arr
        std = np.std(final_port_ret)
        if std == 0: continue
        
        sharpe = np.sqrt(252) * np.mean(excess) / std
        cum = np.cumprod(1 + final_port_ret)
        cummax = np.maximum.accumulate(cum)
        dd = np.min((cum - cummax) / cummax)
        
        if dd > -0.20 and sharpe > best_sharpe:
            best_sharpe = sharpe
            best_params = (fast, slow, vt)
            print(f"New Best: Fast={fast} Slow={slow} VolTarget={vt} | Sharpe={sharpe:.2f} DD={dd:.2%}")

    print(f"BEST FOUND: {best_params} -> Sharpe: {best_sharpe:.2f}")

if __name__ == "__main__":
    run_v8_optimizer()
