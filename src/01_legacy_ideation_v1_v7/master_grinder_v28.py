import pandas as pd
import numpy as np
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

def get_data():
    tickers = ["NVDA", "AAPL", "MSFT", "AMZN", "TLT", "^IRX"]
    df = yf.download(tickers, start="2005-01-01", end="2026-12-31", auto_adjust=False)['Close']
    df = df.ffill().dropna()
    df['RF_Daily'] = ((1 + (df['^IRX'] / 100.0)) ** (1/252)) - 1
    return df

def run_v28():
    df = get_data()
    rets = df.pct_change().fillna(0)
    
    strat_rets = pd.Series(0.0, index=df.index)
    positions = pd.Series('CASH', index=df.index)
    
    stocks = ["NVDA", "AAPL", "MSFT", "AMZN"]
    mom = df[stocks].pct_change(126).fillna(0) # 6 month momentum
    
    lev = 1.0 # 1x leverage, so no borrow cost
    
    for i in range(126, len(df)):
        mom_prev = mom.iloc[i-1]
        tlt_ret_prev = df['TLT'].pct_change(126).iloc[i-1]
        
        # Get stock with highest momentum
        best_stock = mom_prev.idxmax()
        best_mom = mom_prev.max()
        
        if best_mom > 0:
            current_pos = best_stock
        elif tlt_ret_prev > 0:
            current_pos = 'TLT'
        else:
            current_pos = 'CASH'
            
        positions.iloc[i] = current_pos
        
        rf = df['RF_Daily'].iloc[i]
        
        if current_pos == 'CASH':
            strat_rets.iloc[i] = rf
        else:
            strat_rets.iloc[i] = rets[current_pos].iloc[i]
            
        if positions.iloc[i] != positions.iloc[i-1]:
            strat_rets.iloc[i] -= 0.0005 # Slippage
            
    strat_rets = strat_rets.loc['2011-01-01':]
    
    equity = (1 + strat_rets).cumprod()
    days = (equity.index[-1] - equity.index[0]).days
    cagr = (equity.iloc[-1] ** (365.25 / days)) - 1
    mdd = ((equity - equity.cummax()) / equity.cummax()).min()
    
    print(f"--- V28 STOCK ROTATION RESULTS (2011-Present) ---")
    print(f"CAGR: {cagr:.2%}")
    print(f"MDD:  {mdd:.2%}")
    
if __name__ == '__main__':
    run_v28()
