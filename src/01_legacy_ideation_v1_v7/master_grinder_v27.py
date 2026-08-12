import pandas as pd
import numpy as np
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

def get_data():
    tickers = ["QQQ", "TLT", "^VIX", "^IRX"]
    df = yf.download(tickers, start="2000-01-01", end="2026-12-31")['Close']
    df = df.ffill().dropna()
    df['RF_Daily'] = ((1 + (df['^IRX'] / 100.0)) ** (1/252)) - 1
    return df

def run_v27():
    df = get_data()
    rets = df.pct_change().fillna(0)
    
    strat_rets = pd.Series(0.0, index=df.index)
    positions = pd.Series('CASH', index=df.index)
    
    lev = 2.0
    
    vix_sma = df['^VIX'].rolling(20).mean()
    
    for i in range(50, len(df)):
        vix_prev = df['^VIX'].iloc[i-1]
        vix_sma_prev = vix_sma.iloc[i-1]
        
        # If VIX spikes above its 20-day moving average, it's a risk-off signal
        if vix_prev > vix_sma_prev * 1.1:
            current_pos = 'CASH'
        else:
            current_pos = 'QQQ'
            
        positions.iloc[i] = current_pos
        
        rf = df['RF_Daily'].iloc[i]
        borrow_cost = (lev - 1.0) * rf if lev > 1.0 else 0.0
        
        if current_pos == 'CASH':
            strat_rets.iloc[i] = rf
        else:
            strat_rets.iloc[i] = (rets[current_pos].iloc[i] * lev) - borrow_cost
            
        if positions.iloc[i] != positions.iloc[i-1]:
            strat_rets.iloc[i] -= 0.0005 * lev # slippage
            
    strat_rets = strat_rets.loc['2011-01-01':]
    
    equity = (1 + strat_rets).cumprod()
    days = (equity.index[-1] - equity.index[0]).days
    cagr = (equity.iloc[-1] ** (365.25 / days)) - 1
    mdd = ((equity - equity.cummax()) / equity.cummax()).min()
    
    print(f"--- V27 VIX FILTER RESULTS (2011-Present) ---")
    print(f"CAGR: {cagr:.2%}")
    print(f"MDD:  {mdd:.2%}")
    
if __name__ == '__main__':
    run_v27()
