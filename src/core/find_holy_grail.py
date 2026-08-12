import yfinance as yf
import pandas as pd
import numpy as np

def test_risk_parity():
    print("Fetching QQQ, TLT data...")
    df = yf.download(['QQQ', 'TLT'], start='2010-01-01', end='2026-12-31')
    if isinstance(df.columns, pd.MultiIndex):
        close = df['Close']
    else:
        return
        
    ret = close.pct_change()
    
    for q_wt in [0.3, 0.4, 0.5, 0.6]:
        t_wt = 1.0 - q_wt
        
        for lev in [1.5, 2.0, 2.5, 3.0]:
            strat_ret = (q_wt * ret['QQQ'] + t_wt * ret['TLT']) * lev
            strat_ret = strat_ret.loc['2011-07-28':]
            
            equity = (1 + strat_ret).cumprod()
            days = (equity.index[-1] - equity.index[0]).days
            if days < 365: continue
            
            cagr = float((equity.iloc[-1] ** (365.25 / days)) - 1)
            mdd = float(((equity - equity.cummax()) / equity.cummax()).min())
            
            if cagr > 0.18 and mdd > -0.20:
                print(f"FOUND: QQQ_Wt={q_wt}, TLT_Wt={t_wt}, Lev={lev} -> CAGR: {cagr:.2%}, MDD: {mdd:.2%}")

if __name__ == '__main__':
    test_risk_parity()
