import yfinance as yf
import pandas as pd
import numpy as np
import warnings
from itertools import product
warnings.filterwarnings('ignore')

def get_vol_weights(returns, target_vol, month_ends):
    vol20 = returns.rolling(20).std() * np.sqrt(252)
    vol_weights = pd.Series(np.nan, index=returns.index)
    for date in month_ends:
        if date not in vol20.index: continue
        cv = vol20.loc[date]
        if pd.isna(cv) or cv == 0: continue
        vol_weights.loc[date] = min(target_vol / cv, 1.5)
    return vol_weights.ffill().shift(1).fillna(0.0)

def run_optimizer():
    tickers = ['SPY', 'QQQ', 'TLT', 'BTC-USD', '^IRX']
    print(f"[*] Downloading Data for Optimizer...")
    df = yf.download(tickers, start="2014-01-01", end="2024-01-01", auto_adjust=False)['Close']
    df = df.ffill().dropna()
    df = df[df.index.dayofweek < 5]
    
    returns = df.pct_change().dropna()
    daily_cash_yield = (df['^IRX'] / 100) / 252
    daily_cash_yield = daily_cash_yield.fillna(0.0001)
    
    df['YearMonth'] = df.index.to_period('M')
    month_ends = df.groupby('YearMonth').tail(1).index
    valid_idx = returns.index[250:]
    
    r = returns.loc[valid_idx]
    cy = daily_cash_yield.loc[valid_idx]
    
    fast_mas = [10, 20, 50]
    slow_mas = [100, 150, 200]
    vol_targets = [0.05, 0.10, 0.15, 0.20]
    
    best_sharpe = 0
    best_params = None
    
    for fast, slow, vt in product(fast_mas, slow_mas, vol_targets):
        master_weights = pd.DataFrame(0.0, index=df.index, columns=['SPY', 'QQQ', 'TLT', 'BTC-USD'])
        
        for t in ['SPY', 'QQQ', 'TLT', 'BTC-USD']:
            asset = df[t]
            sma_fast = asset.rolling(fast).mean()
            sma_slow = asset.rolling(slow).mean()
            
            trend = (sma_fast > sma_slow).astype(float).shift(1).fillna(0.0)
            vol_w = get_vol_weights(returns[t], vt, month_ends)
            
            master_weights[t] = trend * vol_w * 0.25 # Equal base weight
            
        master_weights = master_weights.loc[valid_idx]
        
        final_port_ret = pd.Series(0.0, index=valid_idx)
        
        delta = master_weights.diff().abs().fillna(0)
        slip = delta * (5 / 10000)
        slip['BTC-USD'] = delta['BTC-USD'] * (30 / 10000)
        slip_total = slip.sum(axis=1)
        
        for date in valid_idx:
            w = master_weights.loc[date]
            gross = w.abs().sum()
            cash = 1.0 - gross
            
            a_ret = (w * r.loc[date][['SPY', 'QQQ', 'TLT', 'BTC-USD']]).sum()
            c_ret = cash * cy.loc[date]
                
            final_port_ret.loc[date] = a_ret + c_ret - slip_total.loc[date]
            
        excess = final_port_ret - cy
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
    run_optimizer()
