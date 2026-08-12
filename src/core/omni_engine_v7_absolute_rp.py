import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

SLIPPAGE_BPS = 5 / 10000

def run_omni_absolute_rp():
    print("[*] Downloading Data for Absolute Risk Parity...")
    tickers = ['SPY', 'TLT', 'GLD', '^IRX']
    df = yf.download(tickers, start="2005-01-01", end="2024-01-01")['Close']
    df = df[~df.index.duplicated(keep='first')]
    df = df.ffill().dropna()
    
    returns = df[['SPY', 'TLT', 'GLD']].pct_change().dropna()
    daily_cash_yield = (df['^IRX'].loc[returns.index] / 100) / 252
    daily_cash_yield = daily_cash_yield.fillna(0.0001)
    
    # Calculate 12-month (252 day) absolute momentum
    mom_252 = df[['SPY', 'TLT', 'GLD']].pct_change(252).shift(1)
    
    # Calculate 60-day rolling volatility for inverse vol weighting
    vol_60 = returns.rolling(60).std() * np.sqrt(252)
    vol_60 = vol_60.shift(1)
    
    weights = pd.DataFrame(0.0, index=returns.index, columns=['SPY', 'TLT', 'GLD'])
    
    df['YearMonth'] = df.index.to_period('M')
    month_ends = df.groupby('YearMonth').tail(1).index
    
    for date in month_ends:
        if date not in vol_60.index or date not in mom_252.index: continue
        vols = vol_60.loc[date]
        moms = mom_252.loc[date]
        
        if vols.isna().any() or moms.isna().any(): continue
            
        inv_vols = 1.0 / vols
        # Apply Absolute Momentum Filter
        for asset in inv_vols.index:
            if moms[asset] < 0:
                inv_vols[asset] = 0.0
                
        total_inv_vol = inv_vols.sum()
        if total_inv_vol > 0:
            weights.loc[date] = inv_vols / total_inv_vol

    weights = weights.ffill().fillna(0.0)
    
    # Execution
    asset_ret = (weights * returns).sum(axis=1)
    gross_exposure = weights.sum(axis=1)
    cash_position = 1.0 - gross_exposure
    cash_ret = cash_position * daily_cash_yield
    
    delta = weights.diff().abs().sum(axis=1).fillna(0)
    port_ret = asset_ret + cash_ret - (delta * SLIPPAGE_BPS)
    
    # Target 10% Volatility
    ENS_TARGET_VOL = 0.10
    ens_vol = port_ret.rolling(60).std() * np.sqrt(252)
    ens_multiplier = pd.Series(1.0, index=port_ret.index)
    
    for date in month_ends:
        if date not in ens_vol.index: continue
        cv = ens_vol.loc[date]
        if pd.isna(cv) or cv == 0: continue
        mult = ENS_TARGET_VOL / cv
        mult = min(mult, 2.0) # Cap at 2x leverage
        ens_multiplier.loc[date] = mult
        
    ens_multiplier = ens_multiplier.ffill().shift(1).fillna(1.0)
    
    final_port_ret = (port_ret * ens_multiplier) - ((ens_multiplier - 1.0).clip(lower=0) * (daily_cash_yield + 0.01/252))
    
    cagr = (1 + final_port_ret).prod() ** (252 / len(final_port_ret)) - 1
    sharpe = np.sqrt(252) * final_port_ret.mean() / (final_port_ret.std() + 1e-9)
    
    cum_ret = (1 + final_port_ret).cumprod()
    max_dd = ((cum_ret - cum_ret.cummax()) / cum_ret.cummax()).min()
    
    print("========================================================")
    print(f"[*] ABSOLUTE RISK PARITY (True Trend + Inverse Vol)")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    
    spy_r = returns['SPY']
    bm_cagr = (1 + spy_r).prod() ** (252 / len(spy_r)) - 1
    bm_sharpe = np.sqrt(252) * spy_r.mean() / (spy_r.std() + 1e-9)
    bm_max_dd = (((1 + spy_r).cumprod() - (1 + spy_r).cumprod().cummax()) / (1 + spy_r).cumprod().cummax()).min()
    print(f"[*] SPY BENCHMARK CAGR: {bm_cagr:.2%} | Sharpe: {bm_sharpe:.2f} | Max DD: {bm_max_dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_omni_absolute_rp()
