"""
OMNI-ALLOCATOR V9: TRI-ASSET INSTITUTIONAL HOLY GRAIL (BTC + GLD + SPY)
-------------------------------------------------------------------------
Allocates capital across:
  - 50% Base Allocation to Bitcoin (BTC-USD)
  - 25% Base Allocation to Gold (GLD)
  - 25% Base Allocation to S&P 500 (SPY)

Integrates all institutional physics and audit fixes:
  1. SPY 252-day business calendar alignment.
  2. Exact weekend borrow & carry accounting (cy_arr * delta_days).
  3. Flawless vector turnover and slippage deduction (20bps BTC, 3bps GLD/SPY).
  4. Option for Hard 1-Bar Execution Lag to eliminate zero-latency lookahead.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def run_omni_allocator_v9():
    print("[*] Launching OMNI-ALLOCATOR V9 (Tri-Asset Holy Grail)...")
    assets = ['BTC-USD', 'GLD', 'SPY']
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
    
    slip_cost = np.array([0.0020, 0.0003, 0.0003])
    alloc = np.array([0.50, 0.25, 0.25])
    vt = 0.15
    
    master_weights = pd.DataFrame(0.0, index=biz_idx, columns=assets)
    for idx_a, t in enumerate(assets):
        c = close_prices[t]
        w_base = alloc[idx_a]
        if t == 'BTC-USD':
            sma_fast = c.rolling(2).mean()
            sma_slow = c.rolling(40).mean()
            trend = (sma_fast > sma_slow).astype(float).shift(1).fillna(0.0)
            vol20 = c.pct_change().rolling(20).std() * np.sqrt(365)
            vol_w = (vt / vol20).clip(upper=1.5).shift(1).fillna(0.0)
            target_weights_365 = trend * vol_w
            master_weights[t] = target_weights_365.ffill().reindex(biz_idx).ffill() * w_base
        else:
            c_biz = c.ffill().reindex(biz_idx).ffill()
            sma_fast = c_biz.rolling(10).mean()
            sma_slow = c_biz.rolling(100).mean()
            trend = (sma_fast > sma_slow).astype(float).shift(1).fillna(0.0)
            vol20 = c_biz.pct_change().rolling(20).std() * np.sqrt(252)
            vol_w = (vt / vol20).clip(upper=1.5).shift(1).fillna(0.0)
            master_weights[t] = trend * vol_w * w_base
            
    for lag in [0, 1]:
        if lag == 0:
            target_w = master_weights.loc[valid_idx].values
            lag_label = "MODE A: STANDARD EXECUTION (0-BAR LAG)"
        else:
            target_w = master_weights.shift(lag).loc[valid_idx].fillna(0.0).values
            lag_label = "MODE B: HARD INSTITUTIONAL EXECUTION (1-BAR LAG)"
            
        final_port_ret = np.zeros(len(valid_idx))
        prev_actual_w = np.zeros(len(assets))
        
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
                prev_actual_w = np.zeros(len(assets))
                
        excess = final_port_ret - (cy_arr * delta_days)
        std = np.std(final_port_ret, ddof=1)
        sharpe = np.sqrt(252) * np.mean(excess) / std
        cagr = np.prod(1 + final_port_ret) ** (252 / len(valid_idx)) - 1
        cum = np.cumprod(1 + final_port_ret)
        cummax = np.maximum.accumulate(cum)
        dd = np.min((cum - cummax) / cummax)
        
        print("=" * 60)
        print(lag_label)
        print("=" * 60)
        print(f"  CAGR:         {cagr:.2%}")
        print(f"  Sharpe Ratio: {sharpe:.2f}")
        print(f"  Max Drawdown: {dd:.2%}")
    print("=" * 60)

if __name__ == "__main__":
    run_omni_allocator_v9()
