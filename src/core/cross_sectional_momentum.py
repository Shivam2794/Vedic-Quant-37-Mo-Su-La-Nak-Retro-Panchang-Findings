import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def run_cross_sectional_momentum():
    tickers = ['XLK', 'XLV', 'XLF', 'XLY', 'XLI', 'XLP', 'XLE', 'XLU', 'XLB', '^IRX'] # Excluded XLC, XLRE due to shorter history
    print(f"[*] Downloading Data for Cross-Sectional Momentum...")
    df = yf.download(tickers, start="2005-01-01", end="2024-01-01")['Close']
    df = df[~df.index.duplicated(keep='first')]
    df = df.ffill().dropna()
    df = df[df.index.dayofweek < 5] # Strict business days
    
    returns = df.pct_change().dropna()
    daily_cash_yield = (df['^IRX'] / 100) / 252
    daily_cash_yield = daily_cash_yield.fillna(0.0001)
    
    # Exclude IRX from momentum ranking
    sectors = [t for t in tickers if t != '^IRX']
    prices = df[sectors]
    
    # 20-day momentum (approx 1 month)
    mom20 = prices.pct_change(20)
    
    master_weights = pd.DataFrame(0.0, index=df.index, columns=sectors)
    
    for i in range(len(df)):
        if i < 20: continue
        
        # Rank sectors by momentum
        row = mom20.iloc[i]
        if row.isna().any(): continue
        
        ranks = row.rank()
        
        # Top 3 long, bottom 3 short.
        # Ranks are 1 to 9. So 1,2,3 are bottom, 7,8,9 are top.
        longs = ranks >= 7
        shorts = ranks <= 3
        
        w = pd.Series(0.0, index=sectors)
        w[longs] = 1.0 / 3.0
        w[shorts] = -1.0 / 3.0
        
        master_weights.iloc[i] = w
        
    # SHIFT TO PREVENT LOOKAHEAD BIAS
    master_weights = master_weights.shift(1).fillna(0.0)
    
    valid_idx = returns.index[25:]
    master_weights = master_weights.loc[valid_idx]
    r = returns.loc[valid_idx][sectors]
    daily_cash_yield = daily_cash_yield.loc[valid_idx]
    
    # We are 100% long and 100% short. Gross exposure is 200%. Net is 0%.
    # Cash position is 100% (since short proceeds pay for longs, plus initial capital).
    # Actually, shorting requires margin and paying the borrow fee.
    borrow_spread = 0.01 / 252 # 100 bps
    
    final_port_ret = pd.Series(0.0, index=valid_idx)
    
    delta = master_weights.diff().abs().fillna(0)
    slip_total = delta.sum(axis=1) * (5 / 10000) # 5bps per trade
    
    for date in valid_idx:
        w = master_weights.loc[date]
        
        a_ret = (w * r.loc[date]).sum()
        
        # Cash return: We have 1.0 initial cash, plus 1.0 from short sale = 2.0 cash.
        # But broker only pays interest on 1.0 (or less). Let's assume we get interest on 1.0 cash.
        # We also pay borrow fee on the 1.0 short.
        c_ret = 1.0 * daily_cash_yield.loc[date]
        borrow_cost = 1.0 * borrow_spread # assuming 100% short
            
        final_port_ret.loc[date] = a_ret + c_ret - borrow_cost - slip_total.loc[date]
        
    excess_ret = final_port_ret - daily_cash_yield
    cagr = (1 + final_port_ret).prod() ** (252 / len(final_port_ret)) - 1
    sharpe = np.sqrt(252) * excess_ret.mean() / (final_port_ret.std() + 1e-9)
    cum_ret = (1 + final_port_ret).cumprod()
    max_dd = ((cum_ret - cum_ret.cummax()) / cum_ret.cummax()).min()
    
    print("========================================================")
    print(f"[*] CROSS-SECTIONAL SECTOR MOMENTUM (L/S)")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_cross_sectional_momentum()
