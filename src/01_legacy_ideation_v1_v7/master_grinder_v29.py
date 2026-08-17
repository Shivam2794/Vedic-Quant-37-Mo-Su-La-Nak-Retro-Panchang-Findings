import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def get_data():
    tickers = ["QQQ", "TLT", "^IRX"]
    df = yf.download(tickers, start="2005-01-01", end="2026-12-31", auto_adjust=False)['Close']
    df = df.ffill().dropna()
    df['RF_Daily'] = ((1 + (df['^IRX'] / 100.0)) ** (1/252)) - 1
    return df

def run_holy_grail():
    df = get_data()
    rets = df.pct_change().fillna(0)
    
    # Core Strategy: 2x Leveraged QQQ / TLT Dual Momentum
    lookback = 60
    mom = df[['QQQ', 'TLT']].pct_change(lookback).fillna(0)
    
    strat_rets = pd.Series(0.0, index=df.index)
    positions = pd.Series('CASH', index=df.index)
    
    lev = 2.0
    
    # Equity Curve Trading State
    high_water_mark = 1.0
    current_equity = 1.0
    in_market = True
    cooldown = 0
    
    for i in range(lookback, len(df)):
        qqq_m = mom['QQQ'].iloc[i-1]
        tlt_m = mom['TLT'].iloc[i-1]
        
        # Core Signal
        if qqq_m > 0 and qqq_m > tlt_m:
            target_pos = 'QQQ'
        elif tlt_m > 0 and tlt_m > qqq_m:
            target_pos = 'TLT'
        else:
            target_pos = 'CASH'
            
        rf = df['RF_Daily'].iloc[i]
        borrow_cost = (lev - 1.0) * rf if lev > 1.0 else 0.0
        
        # Calculate what the return WOULD be
        if target_pos == 'CASH':
            raw_ret = rf
        else:
            raw_ret = (rets[target_pos].iloc[i] * lev) - borrow_cost
            
        # Drawdown protection logic (The Holy Grail Filter)
        if in_market:
            actual_ret = raw_ret
            current_equity *= (1 + actual_ret)
            
            if current_equity > high_water_mark:
                high_water_mark = current_equity
                
            drawdown = (current_equity - high_water_mark) / high_water_mark
            
            # If drawdown hits -15%, pull the plug and go to cash for 60 days
            if drawdown < -0.15:
                in_market = False
                cooldown = 60
                positions.iloc[i] = 'CASH'
                strat_rets.iloc[i] = actual_ret # We take the hit today
                continue
                
            positions.iloc[i] = target_pos
            strat_rets.iloc[i] = actual_ret
            
        else: # Out of market
            cooldown -= 1
            if cooldown <= 0:
                in_market = True
                # Reset high water mark so we don't instantly trip again
                high_water_mark = current_equity 
                
            positions.iloc[i] = 'CASH'
            strat_rets.iloc[i] = rf # Earn risk free rate while sitting out
            
        if positions.iloc[i] != positions.iloc[i-1]:
            strat_rets.iloc[i] -= 0.0005 * lev # Slippage
            
    # Strictly Evaluate 2011 to Present
    strat_rets = strat_rets.loc['2011-01-01':]
    
    equity = (1 + strat_rets).cumprod()
    days = (equity.index[-1] - equity.index[0]).days
    cagr = (equity.iloc[-1] ** (365.25 / days)) - 1
    mdd = ((equity - equity.cummax()) / equity.cummax()).min()
    
    print(f"--- V29 HOLY GRAIL RESULTS (2011-Present) ---")
    print(f"CAGR: {cagr:.2%}")
    print(f"MDD:  {mdd:.2%}")

def run_holy_grail_rets(df):
    rets = df.pct_change().fillna(0)
    lookback = 60
    mom = df[['QQQ', 'TLT']].pct_change(lookback).fillna(0)
    strat_rets = pd.Series(0.0, index=df.index)
    positions = pd.Series('CASH', index=df.index)
    lev = 2.0
    high_water_mark = 1.0
    current_equity = 1.0
    in_market = True
    cooldown = 0
    
    for i in range(lookback, len(df)):
        qqq_m = mom['QQQ'].iloc[i-1]
        tlt_m = mom['TLT'].iloc[i-1]
        
        if qqq_m > 0 and qqq_m > tlt_m: target_pos = 'QQQ'
        elif tlt_m > 0 and tlt_m > qqq_m: target_pos = 'TLT'
        else: target_pos = 'CASH'
            
        rf = df['RF_Daily'].iloc[i]
        borrow_cost = (lev - 1.0) * rf if lev > 1.0 else 0.0
        if target_pos == 'CASH': raw_ret = rf
        else: raw_ret = (rets[target_pos].iloc[i] * lev) - borrow_cost
            
        if in_market:
            actual_ret = raw_ret
            current_equity *= (1 + actual_ret)
            if current_equity > high_water_mark: high_water_mark = current_equity
            drawdown = (current_equity - high_water_mark) / high_water_mark
            if drawdown < -0.15:
                in_market = False
                cooldown = 60
                positions.iloc[i] = 'CASH'
                strat_rets.iloc[i] = actual_ret
                continue
            positions.iloc[i] = target_pos
            strat_rets.iloc[i] = actual_ret
        else:
            cooldown -= 1
            if cooldown <= 0:
                in_market = True
                high_water_mark = current_equity 
            positions.iloc[i] = 'CASH'
            strat_rets.iloc[i] = rf
            
        if positions.iloc[i] != positions.iloc[i-1]:
            strat_rets.iloc[i] -= 0.0005 * lev 
            
    return strat_rets.loc['2011-01-01':]


if __name__ == '__main__':
    run_holy_grail()
