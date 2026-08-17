import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def run_omni_allocator_v8():
    print(f"[*] Downloading Data for Omni-Allocator V8 (The Final Holy Grail)...")
    df_raw = yf.download(['BTC-USD', 'SPY', '^IRX'], start="2014-01-01", end="2024-01-01", progress=False, auto_adjust=False)
    
    # Capture pure business index before ffill
    biz_idx = df_raw['Close']['SPY'].dropna().index
    
    df_raw = df_raw.ffill()
    
    close_prices = df_raw['Close']['BTC-USD']
    open_prices = df_raw['Open']['BTC-USD']
    irx = df_raw['Close']['^IRX']
    
    # ---------------------------------------------------------
    # 1. Native 365-day Math for BTC
    # ---------------------------------------------------------
    sma_fast = close_prices.rolling(2).mean()
    sma_slow = close_prices.rolling(40).mean()
    trend = (sma_fast > sma_slow).astype(float).shift(1).fillna(0.0)
    
    vol20 = close_prices.pct_change().rolling(20).std() * np.sqrt(365)
    vol_w = (0.15 / vol20).clip(upper=1.5).shift(1).fillna(0.0)
    
    # Target Weights on 365-day calendar
    target_weights_365 = trend * vol_w
    
    # ---------------------------------------------------------
    # 2. Filter to 252-day business calendar using pure SPY index
    # ---------------------------------------------------------
    weights_biz = target_weights_365.ffill().reindex(biz_idx).ffill()
    open_biz = open_prices.ffill().reindex(biz_idx).ffill()
    
    # ---------------------------------------------------------
    # 3. Flawless Execution Returns (Friday -> Monday Open captured exactly)
    # ---------------------------------------------------------
    r_open = (open_biz.shift(-1) / open_biz) - 1
    
    # Fix Micro-Lookahead: Shift IRX by 1 day
    irx = irx.ffill().reindex(biz_idx).ffill().shift(1)
    cy = (irx / 100) / 252
    cy = cy.fillna(0.0001)
    
    valid_idx = biz_idx[250:-1]
    
    # Calculate delta_days for margin interest (Friday -> Monday is 3 days)
    # The return at valid_idx[i] goes to valid_idx[i+1]. So delta_days is valid_idx[i+1] - valid_idx[i]
    # We will use biz_idx to calculate delta_days
    delta_days = biz_idx.to_series().diff().shift(-1).dt.days.loc[valid_idx].fillna(1).values
    
    target_w = weights_biz.loc[valid_idx].values
    r_mat = r_open.loc[valid_idx].values
    cy_arr = cy.loc[valid_idx].values
    
    final_port_ret = np.zeros(len(valid_idx))
    prev_actual_w = 0.0
    
    # Slippage: 20 bps for BTC
    slip_cost = 0.0020
    
    # ---------------------------------------------------------
    # 4. Exact Intraday Drift Slippage Simulation
    # ---------------------------------------------------------
    for i in range(len(valid_idx)):
        w = target_w[i]
        
        # Turnover is difference between new target and yesterday's drifted weight
        turnover = np.abs(w - prev_actual_w)
        slip = turnover * slip_cost
        
        cash = 1.0 - np.abs(w)
        a_ret = w * r_mat[i]
        
        # Prime Broker Borrow Cost (Fed Funds + 1.5%) - Multiplied by delta_days for weekend carry
        if cash > 0:
            c_ret = cash * cy_arr[i] * delta_days[i]
        else:
            c_ret = cash * (cy_arr[i] + (0.015 / 252)) * delta_days[i]
            
        port_ret = a_ret + c_ret - slip
        final_port_ret[i] = port_ret
        
        # Calculate drifted actual weight
        if port_ret > -1.0:
            drift_factor = (1.0 + r_mat[i]) / (1.0 + port_ret)
            prev_actual_w = w * drift_factor
        else:
            prev_actual_w = 0.0
            
    excess = final_port_ret - cy_arr
    std = np.std(final_port_ret)
    
    sharpe = np.sqrt(252) * np.mean(excess) / std
    cagr = np.prod(1 + final_port_ret) ** (252 / len(final_port_ret)) - 1
    cum = np.cumprod(1 + final_port_ret)
    cummax = np.maximum.accumulate(cum)
    max_dd = np.min((cum - cummax) / cummax)
    
    print("========================================================")
    print(f"[*] OMNI-ALLOCATOR V8 (The Final Holy Grail)")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_omni_allocator_v8()
