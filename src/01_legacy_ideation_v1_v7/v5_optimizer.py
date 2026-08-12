import yfinance as yf
import pandas as pd
import numpy as np
import warnings
from itertools import product
warnings.filterwarnings('ignore')

def run_v5_optimizer():
    tickers = ['SPY', 'QQQ', 'TLT', 'GLD', 'BTC-USD', 'UUP', 'LQD', '^IRX']
    print(f"[*] Downloading Data for Brutal Physics Optimizer...")
    # Get Open and Close
    df_raw = yf.download(tickers, start="2014-01-01", end="2024-01-01")
    
    close_prices = df_raw['Close'].ffill().dropna()
    open_prices = df_raw['Open'].ffill().dropna()
    
    # 1. Native BTC Math (365 day) before aligning
    btc_close_native = close_prices['BTC-USD']
    
    # Align to TradFi business days
    biz_idx = close_prices[close_prices.index.dayofweek < 5].index
    
    cy = (close_prices['^IRX'].loc[biz_idx] / 100) / 252
    cy = cy.fillna(0.0001)
    
    fast_mas = [10, 15, 20]
    slow_mas = [100, 150, 200]
    vol_targets = [0.10, 0.15, 0.20, 0.25]
    
    best_sharpe = 0
    best_params = None
    
    for fast, slow, vt in product(fast_mas, slow_mas, vol_targets):
        
        master_weights = pd.DataFrame(0.0, index=biz_idx, columns=['SPY', 'QQQ', 'TLT', 'GLD', 'BTC-USD', 'UUP', 'LQD'])
        
        for t in ['SPY', 'QQQ', 'TLT', 'GLD', 'BTC-USD', 'UUP', 'LQD']:
            if t == 'BTC-USD':
                # Calculate natively, then reindex
                sma_fast = btc_close_native.rolling(fast).mean()
                sma_slow = btc_close_native.rolling(slow).mean()
                trend = (sma_fast > sma_slow).astype(float)
                trend = trend.reindex(biz_idx).ffill().shift(1).fillna(0.0)
                
                # Daily volatility targeting
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
                
            master_weights[t] = trend * vol_w * 0.1428 # Equal base weight
            
        valid_idx = biz_idx[250:]
        master_weights = master_weights.loc[valid_idx]
        
        # Open-to-Open Returns (Execution on Open)
        # return on day T = (Open_{T+1} - Open_{T}) / Open_{T}
        o = open_prices.loc[valid_idx]
        open_returns = o.pct_change().shift(-1).fillna(0) # This captures the return from today's open to tomorrow's open
        # Wait, if we generate signal on T close, we enter on T+1 open.
        # The return is from T+1 open to T+2 open.
        # So we use master_weights.loc[T], which is the weight FOR T+1 based on data up to T.
        # The return it earns is open_returns.loc[T+1].
        
        # Let's align it simply:
        # master_weights.loc[T] is the position we take AT the open of T. 
        # (It used data up to T-1).
        # We hold it until the open of T+1.
        # The return earned is (Open_T+1 / Open_T) - 1.
        r_open = (open_prices.shift(-1) / open_prices) - 1
        r_open = r_open.loc[valid_idx]
        
        final_port_ret = pd.Series(0.0, index=valid_idx)
        
        # Exact Weight Drift calculation is too slow for python loop, use approx delta
        delta = master_weights.diff().abs().fillna(0)
        slip = delta * (3 / 10000) # 3bps slippage
        slip['BTC-USD'] = delta['BTC-USD'] * (20 / 10000) # 20bps
        slip_total = slip.sum(axis=1)
        
        # Vectorized portfolio returns
        gross = master_weights.abs().sum(axis=1)
        cash = 1.0 - gross
        
        a_ret = (master_weights * r_open[['SPY', 'QQQ', 'TLT', 'GLD', 'BTC-USD', 'UUP', 'LQD']]).sum(axis=1)
        
        # Borrow cost: IRX + 1.5%
        borrow_cost = cy.loc[valid_idx] + (0.015 / 252)
        c_ret = np.where(cash > 0, cash * cy.loc[valid_idx], cash * borrow_cost)
        
        final_port_ret = a_ret + c_ret - slip_total
        
        excess = final_port_ret - cy.loc[valid_idx]
        std = final_port_ret.std()
        if std == 0: continue
        
        sharpe = np.sqrt(252) * excess.mean() / std
        cum = (1 + final_port_ret).cumprod()
        dd = ((cum - cum.cummax()) / cum.cummax()).min()
        
        if dd > -0.20 and sharpe > best_sharpe:
            best_sharpe = sharpe
            best_params = (fast, slow, vt)
            print(f"New Best: Fast={fast} Slow={slow} VolTarget={vt} | Sharpe={sharpe:.2f} DD={dd:.2%}")
            
    print(f"BEST FOUND: {best_params} -> Sharpe: {best_sharpe:.2f}")

if __name__ == "__main__":
    run_v5_optimizer()
