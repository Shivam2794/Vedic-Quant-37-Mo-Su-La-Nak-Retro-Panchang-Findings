import yfinance as yf
import pandas as pd
import numpy as np
import warnings
from itertools import product
warnings.filterwarnings('ignore')

def run_v7_optimizer():
    tickers = ['SPY', 'QQQ', 'IWM', 'EFA', 'EEM', 'TLT', 'IEF', 'SHY', 'LQD', 'HYG', 'GLD', 'SLV', 'VNQ', 'UUP', 'BTC-USD', '^IRX']
    print(f"[*] Downloading Data for Massive Diversified Optimizer...")
    
    # Download data
    df_raw = yf.download(tickers, start="2014-01-01", end="2024-01-01", progress=False)
    close_prices = df_raw['Close'].ffill().dropna()
    open_prices = df_raw['Open'].ffill().dropna()
    
    # 1. Native BTC Math (365 day) before aligning
    btc_close_native = close_prices['BTC-USD']
    
    # Filter to strict 252-day business calendar FIRST
    biz_idx = close_prices[close_prices.index.dayofweek < 5].index
    
    # 2. Fix Weekend Gap Erasure: Calculate open returns AFTER dropping weekends
    open_biz = open_prices.loc[biz_idx]
    r_open = (open_biz.shift(-1) / open_biz) - 1
    
    cy = (close_prices['^IRX'].loc[biz_idx] / 100) / 252
    cy = cy.fillna(0.0001)
    
    # Use standard institutional parameters
    fast_mas = [10, 20, 50]
    slow_mas = [100, 150, 200]
    vol_targets = [0.05, 0.10, 0.15]
    
    best_sharpe = 0
    best_params = None
    
    assets = [t for t in tickers if t != '^IRX']
    num_assets = len(assets)
    base_w = 1.0 / num_assets
    
    valid_idx = biz_idx[250:-1] # Drop last row because shift(-1) is NaN
    r_open = r_open.loc[valid_idx]
    cy = cy.loc[valid_idx]
    
    for fast, slow, vt in product(fast_mas, slow_mas, vol_targets):
        
        master_weights = pd.DataFrame(0.0, index=biz_idx, columns=assets)
        
        for t in assets:
            if t == 'BTC-USD':
                # Calculate natively, then reindex
                sma_fast = btc_close_native.rolling(fast).mean()
                sma_slow = btc_close_native.rolling(slow).mean()
                trend = (sma_fast > sma_slow).astype(float)
                trend = trend.reindex(biz_idx).ffill().shift(1).fillna(0.0)
                
                vol20 = btc_close_native.pct_change().rolling(20).std() * np.sqrt(365)
                vol_w = (vt / vol20).clip(upper=1.5)
                vol_w = vol_w.reindex(biz_idx).ffill().shift(1).fillna(0.0)
            else:
                c = close_prices[t].loc[biz_idx]
                sma_fast = c.rolling(fast).mean()
                sma_slow = c.rolling(slow).mean()
                trend = (sma_fast > sma_slow).astype(float).shift(1).fillna(0.0)
                
                vol20 = c.pct_change().rolling(20).std() * np.sqrt(252)
                vol_w = (vt / vol20).clip(upper=1.5).shift(1).fillna(0.0)
                
            master_weights[t] = trend * vol_w * base_w
            
        weights = master_weights.loc[valid_idx]
        
        final_port_ret = np.zeros(len(valid_idx))
        
        # 3. Fix Exact Weight Drift Slippage
        # Convert DataFrames to numpy for fast loop
        w_mat = weights.values
        r_mat = r_open[assets].values
        cy_arr = cy.values
        
        # Slippage assumes 3bps for standard ETFs, 20bps for BTC
        slip_cost = np.full(num_assets, 0.0003)
        btc_idx = assets.index('BTC-USD')
        slip_cost[btc_idx] = 0.0020
        
        prev_actual_w = np.zeros(num_assets)
        
        for i in range(len(valid_idx)):
            target_w = w_mat[i]
            
            # Turnover is diff between target and actual drift from yesterday
            turnover = np.abs(target_w - prev_actual_w)
            slip = np.sum(turnover * slip_cost)
            
            gross = np.sum(np.abs(target_w))
            cash = 1.0 - gross
            
            asset_rets = target_w * r_mat[i]
            a_ret = np.sum(asset_rets)
            
            # Borrow cost: IRX + 1.5%
            if cash > 0:
                c_ret = cash * cy_arr[i]
            else:
                c_ret = cash * (cy_arr[i] + (0.015 / 252))
                
            port_ret = a_ret + c_ret - slip
            final_port_ret[i] = port_ret
            
            # Calculate actual drifted weight for end of day
            if port_ret > -1.0:
                drift_factor = (1.0 + r_mat[i]) / (1.0 + port_ret)
                prev_actual_w = target_w * drift_factor
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
    run_v7_optimizer()
