import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

SLIPPAGE_BPS = 10 / 10000

def run_omni_vrp_optimized():
    print("[*] Downloading Data for Optimized VRP...")
    tickers = ['SVXY', 'VIXY', '^VIX', '^VIX3M', 'SHV', 'SPY']
    df = yf.download(tickers, start="2012-01-01", end="2024-01-01")['Close']
    df = df[~df.index.duplicated(keep='first')]
    df = df.ffill().dropna()
    
    returns = df.pct_change().dropna()
    r = returns
    
    term_structure = df['^VIX'] / df['^VIX3M']
    vix = df['^VIX']
    
    svxy_sma10 = df['SVXY'].rolling(10).mean()
    vixy_sma5 = df['VIXY'].rolling(5).mean()
    
    weights = pd.DataFrame(0.0, index=df.index, columns=['SVXY', 'VIXY', 'SHV'])
    
    for i in range(10, len(df)):
        date = df.index[i]
        ts = term_structure.iloc[i]
        v = vix.iloc[i]
        
        svxy_price = df['SVXY'].iloc[i]
        vixy_price = df['VIXY'].iloc[i]
        
        if pd.isna(ts) or pd.isna(v):
            weights.loc[date, 'SHV'] = 1.0
            continue
            
        # VRP Logic
        if ts < 0.92 and v < 22:
            # Short Volatility Regime (Contango + Calm Market)
            if svxy_price > svxy_sma10.iloc[i]:
                weights.loc[date, 'SVXY'] = 1.0
            else:
                weights.loc[date, 'SHV'] = 1.0
        elif ts > 1.05:
            # Long Volatility Regime (Backwardation / Panic)
            if vixy_price > vixy_sma5.iloc[i]:
                weights.loc[date, 'VIXY'] = 1.0
            else:
                weights.loc[date, 'SHV'] = 1.0
        else:
            weights.loc[date, 'SHV'] = 1.0

    # Shift to prevent look-ahead bias
    weights = weights.shift(1).fillna(0.0)
    
    valid_idx = weights.index[20:]
    weights = weights.loc[valid_idx]
    r = returns.loc[valid_idx]
    
    # Apply weights
    port_ret = (weights['SVXY'] * r['SVXY']) + (weights['VIXY'] * r['VIXY']) + (weights['SHV'] * (0.02/252))
    
    # Slippage
    delta = weights.diff().abs().sum(axis=1).fillna(0)
    port_ret -= (delta * SLIPPAGE_BPS)
    
    # ---------------------------------------------------------
    # VOLATILITY TARGETING
    # ---------------------------------------------------------
    ENS_TARGET_VOL = 0.12 # Target 12% Vol
    ens_vol = port_ret.rolling(20).std() * np.sqrt(252)
    ens_multiplier = pd.Series(1.0, index=port_ret.index)
    
    for i in range(len(port_ret)):
        if pd.isna(ens_vol.iloc[i]) or ens_vol.iloc[i] == 0: continue
        mult = ENS_TARGET_VOL / ens_vol.iloc[i]
        mult = min(mult, 1.5) # Max 1.5x portfolio leverage
        ens_multiplier.iloc[i] = mult
        
    ens_multiplier = ens_multiplier.shift(1).fillna(1.0)
    final_port_ret = port_ret * ens_multiplier - (ens_multiplier - 1.0).clip(lower=0) * (0.02/252)
    
    cagr = (1 + final_port_ret).prod() ** (252 / len(final_port_ret)) - 1
    sharpe = np.sqrt(252) * final_port_ret.mean() / (final_port_ret.std() + 1e-9)
    
    cum_ret = (1 + final_port_ret).cumprod()
    max_dd = ((cum_ret - cum_ret.cummax()) / cum_ret.cummax()).min()
    
    print("========================================================")
    print(f"[*] VRP OPTIMIZED (Momentum + Contango Filter)")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    
    spy_r = r['SPY']
    bm_cagr = (1 + spy_r).prod() ** (252 / len(spy_r)) - 1
    bm_sharpe = np.sqrt(252) * spy_r.mean() / (spy_r.std() + 1e-9)
    bm_max_dd = (((1 + spy_r).cumprod() - (1 + spy_r).cumprod().cummax()) / (1 + spy_r).cumprod().cummax()).min()
    print(f"[*] SPY BENCHMARK CAGR: {bm_cagr:.2%} | Sharpe: {bm_sharpe:.2f} | Max DD: {bm_max_dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_omni_vrp_optimized()
