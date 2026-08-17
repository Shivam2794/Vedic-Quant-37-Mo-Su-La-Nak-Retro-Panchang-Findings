import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def run_path1_latency_test():
    print("[*] PATH 1: Institutional Latency & Execution Stress Test...")
    df_raw = yf.download(['BTC-USD', 'SPY', '^IRX'], start="2014-01-01", end="2024-01-01", progress=False, auto_adjust=False)
    
    biz_idx = df_raw['Close']['SPY'].dropna().index
    df_raw = df_raw.ffill()
    
    close_prices = df_raw['Close']['BTC-USD']
    open_prices = df_raw['Open']['BTC-USD']
    irx = df_raw['Close']['^IRX']
    
    # 1. Native 365-day Math for BTC
    sma_fast = close_prices.rolling(2).mean()
    sma_slow = close_prices.rolling(40).mean()
    trend = (sma_fast > sma_slow).astype(float).shift(1).fillna(0.0)
    
    vol20 = close_prices.pct_change().rolling(20).std() * np.sqrt(365)
    vol_w = (0.15 / vol20).clip(upper=1.5).shift(1).fillna(0.0)
    
    target_weights_365 = trend * vol_w
    
    # 2. Filter to 252-day business calendar
    weights_biz = target_weights_365.ffill().reindex(biz_idx).ffill()
    open_biz = open_prices.ffill().reindex(biz_idx).ffill()
    
    # Returns from Open(t+1) to Open(t+2)
    r_open = (open_biz.shift(-1) / open_biz) - 1
    
    irx = irx.ffill().reindex(biz_idx).ffill().shift(1)
    cy = (irx / 100) / 252
    cy = cy.fillna(0.0001)
    
    valid_idx = biz_idx[250:-1]
    delta_days = biz_idx.to_series().diff().shift(-1).dt.days.loc[valid_idx].fillna(1).values
    
    r_mat = r_open.loc[valid_idx].values
    cy_arr = cy.loc[valid_idx].values
    slip_cost = 0.0020
    
    # We will test two modes:
    # Mode A: Standard V8 (Decision at Close(t-1), Execute at Open(t), Return Open(t)->Open(t+1))
    # Mode B: 1-Bar Execution Lag (Decision at Close(t-1), Execute at Open(t+1), Return Open(t+1)->Open(t+2))
    
    for mode_name, lag_shift in [("Mode A (0-Bar Lag - V8 Standard)", 0), ("Mode B (1-Bar Hard Institutional Lag)", 1)]:
        if lag_shift == 0:
            target_w = weights_biz.loc[valid_idx].values
        else:
            target_w = weights_biz.shift(lag_shift).loc[valid_idx].fillna(0.0).values
            
        final_port_ret = np.zeros(len(valid_idx))
        prev_actual_w = 0.0
        
        for i in range(len(valid_idx)):
            w = target_w[i]
            turnover = np.abs(w - prev_actual_w)
            slip = turnover * slip_cost
            cash = 1.0 - np.abs(w)
            a_ret = w * r_mat[i]
            
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
                prev_actual_w = 0.0
                
        # Corrected Excess Return subtracting weekend delta_days!
        excess = final_port_ret - (cy_arr * delta_days)
        std = np.std(final_port_ret, ddof=1)
        sharpe = np.sqrt(252) * np.mean(excess) / std
        cagr = np.prod(1 + final_port_ret) ** (252 / len(final_port_ret)) - 1
        cum = np.cumprod(1 + final_port_ret)
        cummax = np.maximum.accumulate(cum)
        max_dd = np.min((cum - cummax) / cummax)
        
        print("-" * 55)
        print(f"[{mode_name}]")
        print(f"CAGR:      {cagr:.2%}")
        print(f"Sharpe:    {sharpe:.2f}")
        print(f"Max DD:    {max_dd:.2%}")
    print("-" * 55)

if __name__ == "__main__":
    run_path1_latency_test()
