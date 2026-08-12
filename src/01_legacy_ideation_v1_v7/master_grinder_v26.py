import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def get_data():
    tickers = ["QQQ", "TLT", "^IRX"]
    df = yf.download(tickers, start="2000-01-01", end="2026-12-31")['Close']
    df = df.ffill().dropna()
    df['RF_Daily'] = ((1 + (df['^IRX'] / 100.0)) ** (1/252)) - 1
    return df

def run_v26_fixed():
    df = get_data()
    rets = df.pct_change().fillna(0)
    
    # Simple Fixed Trend Rule
    sma_20 = df['QQQ'].rolling(20).mean()
    sma_50 = df['QQQ'].rolling(50).mean()
    
    strat_rets = pd.Series(0.0, index=df.index)
    positions = pd.Series('CASH', index=df.index)
    
    lev = 2.0  # 2x Leverage
    
    for i in range(200, len(df)):
        qqq_price_prev = df['QQQ'].iloc[i-1]
        qqq_sma_prev = sma_50.iloc[i-1]
        
        tlt_price_prev = df['TLT'].iloc[i-1]
        tlt_sma_prev = df['TLT'].rolling(50).mean().iloc[i-1]
        
        if qqq_price_prev > qqq_sma_prev:
            current_pos = 'QQQ'
        elif tlt_price_prev > tlt_sma_prev:
            current_pos = 'TLT'
        else:
            current_pos = 'CASH'
            
        positions.iloc[i] = current_pos
        
        rf = df['RF_Daily'].iloc[i]
        borrow_cost = (lev - 1.0) * rf if lev > 1.0 else 0.0
        
        if current_pos == 'CASH':
            strat_rets.iloc[i] = rf
        else:
            strat_rets.iloc[i] = (rets[current_pos].iloc[i] * lev) - borrow_cost
            
        if positions.iloc[i] != positions.iloc[i-1]:
            strat_rets.iloc[i] -= 0.0005 * lev # slippage
            
    # Evaluate strictly 2011-01-01 to Present
    strat_rets = strat_rets.loc['2011-01-01':]
    
    equity = (1 + strat_rets).cumprod()
    days = (equity.index[-1] - equity.index[0]).days
    cagr = (equity.iloc[-1] ** (365.25 / days)) - 1
    mdd = ((equity - equity.cummax()) / equity.cummax()).min()
    
    print(f"--- V26 FIXED RULE RESULTS (2011-Present) ---")
    print(f"CAGR: {cagr:.2%}")
    print(f"MDD:  {mdd:.2%}")
    
if __name__ == '__main__':
    run_v26_fixed()
