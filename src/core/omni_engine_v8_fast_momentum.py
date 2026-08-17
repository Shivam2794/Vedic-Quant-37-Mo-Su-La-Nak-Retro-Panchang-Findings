import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def run_fast_momentum():
    print("[*] Downloading Data for Fast Dual Momentum...")
    tickers = ['QQQ', 'TLT', 'GLD', 'SHV']
    df = yf.download(tickers, start="2005-01-01", end="2024-01-01", auto_adjust=False)['Close']
    df = df.ffill().dropna()
    
    returns = df.pct_change().dropna()
    
    # 20-day momentum (1 month)
    mom_20 = df.pct_change(20).shift(1)
    
    weights = pd.DataFrame(0.0, index=df.index, columns=['QQQ', 'TLT', 'GLD', 'SHV'])
    
    # Rebalance weekly
    df['Week'] = df.index.isocalendar().week
    df['Year'] = df.index.isocalendar().year
    week_ends = df.groupby(['Year', 'Week']).tail(1).index
    
    for date in week_ends:
        if date not in mom_20.index: continue
        moms = mom_20.loc[date]
        if moms.isna().any(): continue
            
        qqq_mom = moms['QQQ']
        tlt_mom = moms['TLT']
        gld_mom = moms['GLD']
        
        # Select the asset with the highest momentum
        best_asset = 'SHV'
        best_mom = 0
        
        if qqq_mom > best_mom:
            best_asset = 'QQQ'
            best_mom = qqq_mom
        if tlt_mom > best_mom:
            best_asset = 'TLT'
            best_mom = tlt_mom
        if gld_mom > best_mom:
            best_asset = 'GLD'
            best_mom = gld_mom
            
        weights.loc[date, best_asset] = 1.0

    weights = weights.ffill().fillna(0.0)
    
    port_ret = (weights * returns).sum(axis=1)
    
    # Target 15% Volatility
    ENS_TARGET_VOL = 0.15
    ens_vol = port_ret.rolling(20).std() * np.sqrt(252)
    ens_multiplier = pd.Series(1.0, index=port_ret.index)
    
    for date in week_ends:
        if date not in ens_vol.index: continue
        cv = ens_vol.loc[date]
        if pd.isna(cv) or cv == 0: continue
        mult = ENS_TARGET_VOL / cv
        mult = min(mult, 2.0)
        ens_multiplier.loc[date] = mult
        
    ens_multiplier = ens_multiplier.ffill().shift(1).fillna(1.0)
    
    final_port_ret = (port_ret * ens_multiplier)
    
    cagr = (1 + final_port_ret).prod() ** (252 / len(final_port_ret)) - 1
    sharpe = np.sqrt(252) * final_port_ret.mean() / (final_port_ret.std() + 1e-9)
    
    cum_ret = (1 + final_port_ret).cumprod()
    max_dd = ((cum_ret - cum_ret.cummax()) / cum_ret.cummax()).min()
    
    print("========================================================")
    print(f"[*] FAST DUAL MOMENTUM")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_fast_momentum()
