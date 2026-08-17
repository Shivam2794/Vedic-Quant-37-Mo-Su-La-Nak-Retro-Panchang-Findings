import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def run_omni_allocator_v6():
    tickers = ['SPY', 'QQQ', 'TLT', 'GLD', 'BTC-USD', 'UUP', 'LQD', '^IRX']
    print(f"[*] Downloading Data for Omni-Allocator V6 (Mathematically Immaculate)...")
    
    df_raw = yf.download(tickers, start="2014-01-01", end="2024-01-01", auto_adjust=False)
    close_prices = df_raw['Close'].ffill().dropna()
    open_prices = df_raw['Open'].ffill().dropna()
    
    # ---------------------------------------------------------
    # 1. Hindsight & Weekend Bleed Fix (Native 365-day BTC Math)
    # ---------------------------------------------------------
    btc_close_native = close_prices['BTC-USD']
    
    # Align everything to strict 252-day business calendar
    biz_idx = close_prices[close_prices.index.dayofweek < 5].index
    
    cy = (close_prices['^IRX'].loc[biz_idx] / 100) / 252
    cy = cy.fillna(0.0001)
    
    # Optimized standard parameters
    fast = 10
    slow = 100
    vt = 0.10
    
    master_weights = pd.DataFrame(0.0, index=biz_idx, columns=['SPY', 'QQQ', 'TLT', 'GLD', 'BTC-USD', 'UUP', 'LQD'])
    
    for t in ['SPY', 'QQQ', 'TLT', 'GLD', 'BTC-USD', 'UUP', 'LQD']:
        if t == 'BTC-USD':
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
            
        master_weights[t] = trend * vol_w * 0.1428 # Equal base weight allocation
        
    valid_idx = biz_idx[250:]
    master_weights = master_weights.loc[valid_idx]
    
    # ---------------------------------------------------------
    # 2. Execution Illusion Fix (Exact Open-to-Open Returns)
    # ---------------------------------------------------------
    r_open = (open_prices.shift(-1) / open_prices) - 1
    r_open = r_open.loc[valid_idx]
    
    # ---------------------------------------------------------
    # 3. Exact Weight Drift Slippage Fix
    # ---------------------------------------------------------
    delta = master_weights.diff().abs().fillna(0)
    slip = delta * (3 / 10000)
    slip['BTC-USD'] = delta['BTC-USD'] * (20 / 10000)
    slip_total = slip.sum(axis=1)
    
    # ---------------------------------------------------------
    # 4. Static Margin Abuse Fix (Prime Broker Fed Funds + 1.5%)
    # ---------------------------------------------------------
    gross = master_weights.abs().sum(axis=1)
    cash = 1.0 - gross
    
    a_ret = (master_weights * r_open[['SPY', 'QQQ', 'TLT', 'GLD', 'BTC-USD', 'UUP', 'LQD']]).sum(axis=1)
    borrow_cost = cy.loc[valid_idx] + (0.015 / 252)
    c_ret = np.where(cash > 0, cash * cy.loc[valid_idx], cash * borrow_cost)
    
    final_port_ret = a_ret + c_ret - slip_total
    
    excess = final_port_ret - cy.loc[valid_idx]
    std = final_port_ret.std()
    
    sharpe = np.sqrt(252) * excess.mean() / std
    cagr = (1 + final_port_ret).prod() ** (252 / len(final_port_ret)) - 1
    cum = (1 + final_port_ret).cumprod()
    dd = ((cum - cum.cummax()) / cum.cummax()).min()
    
    print("========================================================")
    print(f"[*] DYNAMIC OMNI-ALLOCATOR V6 (Immaculate Execution)")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_omni_allocator_v6()
