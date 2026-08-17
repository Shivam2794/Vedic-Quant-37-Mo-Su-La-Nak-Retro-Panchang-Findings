import yfinance as yf
import pandas as pd
import numpy as np
from itertools import product
import warnings
warnings.filterwarnings('ignore')

def run_fine_optimizer():
    df_raw = yf.download(['BTC-USD', 'SPY', '^IRX'], start="2014-01-01", end="2024-01-01", progress=False, auto_adjust=False)
    df_raw = df_raw.ffill()
    
    close_prices = df_raw['Close']['BTC-USD']
    open_prices = df_raw['Open']['BTC-USD']
    spy_close = df_raw['Close']['SPY'].dropna()
    irx = df_raw['Close']['^IRX']
    
    biz_idx = spy_close.index
    open_biz = open_prices.ffill().reindex(biz_idx).ffill()
    r_open = (open_biz.shift(-1) / open_biz) - 1
    
    irx = irx.ffill().reindex(biz_idx).ffill().shift(1)
    cy = (irx / 100) / 252
    cy = cy.fillna(0.0001)
    
    valid_idx = biz_idx[250:-1]
    
    r_mat = r_open.loc[valid_idx].values
    cy_arr = cy.loc[valid_idx].values
    slip_cost = 0.0020
    
    fast_mas = range(2, 11)
    slow_mas = range(20, 101, 10)
    vol_targets = np.arange(0.05, 0.21, 0.01)
    
    best_sharpe = 0
    best_params = None
    
    for fast, slow, vt in product(fast_mas, slow_mas, vol_targets):
        if fast >= slow: continue
        sma_fast = close_prices.rolling(fast).mean()
        sma_slow = close_prices.rolling(slow).mean()
        trend = (sma_fast > sma_slow).astype(float).shift(1).fillna(0.0)
        
        vol20 = close_prices.pct_change().rolling(20).std() * np.sqrt(365)
        vol_w = (vt / vol20).clip(upper=1.5).shift(1).fillna(0.0)
        
        target_weights_365 = trend * vol_w
        weights_biz = target_weights_365.ffill().reindex(biz_idx).ffill()
        
        target_w = weights_biz.loc[valid_idx].values
        
        final_port_ret = np.zeros(len(valid_idx))
        prev_actual_w = 0.0
        
        for i in range(len(valid_idx)):
            w = target_w[i]
            turnover = np.abs(w - prev_actual_w)
            slip = turnover * slip_cost
            cash = 1.0 - np.abs(w)
            a_ret = w * r_mat[i]
            
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
                prev_actual_w = 0.0
                
        std = np.std(final_port_ret)
        if std == 0: continue
        
        excess = final_port_ret - cy_arr
        sharpe = np.sqrt(252) * np.mean(excess) / std
        
        if sharpe > best_sharpe:
            best_sharpe = sharpe
            best_params = (fast, slow, vt)
            print(f"New Best: {best_params} | Sharpe={sharpe:.3f}")

if __name__ == "__main__":
    run_fine_optimizer()
