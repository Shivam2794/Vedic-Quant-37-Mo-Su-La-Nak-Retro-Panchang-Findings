import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

SLIPPAGE_BPS = 20 / 10000

def run_omni_orca():
    print("[*] Downloading Data for ORCA (Online Regime Correlation Analyzer)...")
    tickers = ['UPRO', 'TMF', 'SPY', 'TLT', 'SHV']
    df = yf.download(tickers, start="2010-01-01", end="2024-01-01", auto_adjust=False)['Close']
    df = df[~df.index.duplicated(keep='first')]
    df = df.ffill().dropna()
    
    returns = df.pct_change().dropna()
    daily_cash_yield = 0.02 / 252
    
    # ---------------------------------------------------------
    # ORCA: Correlation Regime Detection
    # ---------------------------------------------------------
    print("[*] Calculating Rolling Cross-Asset Covariance...")
    
    spy_ret = returns['SPY']
    tlt_ret = returns['TLT']
    if isinstance(spy_ret, pd.DataFrame): spy_ret = spy_ret.iloc[:, 0]
    if isinstance(tlt_ret, pd.DataFrame): tlt_ret = tlt_ret.iloc[:, 0]
        
    # Calculate 40-day rolling correlation between Stocks (SPY) and Bonds (TLT)
    rolling_corr = spy_ret.rolling(window=40).corr(tlt_ret)
    
    weights = pd.DataFrame(0.0, index=returns.index, columns=['UPRO', 'TMF', 'SHV'])
    
    # Target allocations
    upro_target = 0.55
    tmf_target = 0.45
    
    for i in range(40, len(returns)):
        date = returns.index[i]
        corr = rolling_corr.iloc[i]
        
        if pd.isna(corr):
            weights.loc[date, 'SHV'] = 1.0
            continue
            
        # The ORCA Rule: 
        # If correlation is positive, it means bonds are not protecting stocks (Contagion/Inflation Regime).
        # We must flee to cash.
        if corr > 0.10: 
            weights.loc[date, 'SHV'] = 1.0
        else:
            # Safe Regime: Deploy Leveraged Risk Parity
            weights.loc[date, 'UPRO'] = upro_target
            weights.loc[date, 'TMF'] = tmf_target

    # Shift to prevent look-ahead bias
    weights = weights.shift(1).fillna(0.0)
    
    # ---------------------------------------------------------
    # EXECUTION & TRUE MARGIN ACCOUNTING
    # ---------------------------------------------------------
    valid_idx = weights.index[200:]
    weights = weights.loc[valid_idx]
    r = returns.loc[valid_idx]
    
    asset_ret = (weights['UPRO'] * r['UPRO']) + (weights['TMF'] * r['TMF'])
    
    gross_exposure = weights[['UPRO', 'TMF']].sum(axis=1)
    cash_position = 1.0 - gross_exposure
    
    cash_ret = pd.Series(0.0, index=valid_idx)
    for date, cash in cash_position.items():
        if cash > 0:
            cash_ret.loc[date] = cash * daily_cash_yield
        else:
            cash_ret.loc[date] = cash * (daily_cash_yield + (0.01/252)) # 1% borrow spread
            
    # Slippage
    delta = weights.diff().abs().fillna(0)
    total_slippage = (delta['UPRO'] * SLIPPAGE_BPS) + (delta['TMF'] * SLIPPAGE_BPS)
    
    port_ret = asset_ret + cash_ret - total_slippage
    
    # ---------------------------------------------------------
    # VOLATILITY TARGETING TO PROTECT MAX DD
    # ---------------------------------------------------------
    ENS_TARGET_VOL = 0.15 # 15% Volatility Target
    ens_vol = port_ret.rolling(20).std() * np.sqrt(252)
    ens_multiplier = pd.Series(1.0, index=port_ret.index)
    
    # Update volatility targeting monthly to reduce turnover
    df['YearMonth'] = df.index.to_period('M')
    month_ends = df.groupby('YearMonth').tail(1).index
    
    for date in month_ends:
        if date not in ens_vol.index: continue
        cv = ens_vol.loc[date]
        if pd.isna(cv) or cv == 0: continue
            
        mult = ENS_TARGET_VOL / cv
        mult = min(mult, 1.5) # Max 1.5x portfolio leverage
        ens_multiplier.loc[date] = mult
        
    ens_multiplier = ens_multiplier.ffill().shift(1).fillna(1.0)
    
    # Apply dynamic ensemble multiplier
    final_port_ret = pd.Series(0.0, index=valid_idx)
    
    for i, date in enumerate(valid_idx):
        mult = ens_multiplier.loc[date]
        w = weights.loc[date] * mult
        gross = w[['UPRO', 'TMF']].sum()
        cash = 1.0 - gross
        
        a_ret = (w['UPRO'] * r.loc[date, 'UPRO']) + (w['TMF'] * r.loc[date, 'TMF'])
        
        if cash > 0:
            c_ret = cash * daily_cash_yield
        else:
            c_ret = cash * (daily_cash_yield + (0.01/252))
            
        if i > 0:
            prev_w = weights.loc[valid_idx[i-1]] * ens_multiplier.loc[valid_idx[i-1]]
            d = (w - prev_w).abs()
            s = (d['UPRO'] * SLIPPAGE_BPS) + (d['TMF'] * SLIPPAGE_BPS)
        else:
            s = 0.0
            
        final_port_ret.loc[date] = a_ret + c_ret - s
    
    cagr = (1 + final_port_ret).prod() ** (252 / len(final_port_ret)) - 1
    sharpe = np.sqrt(252) * final_port_ret.mean() / (final_port_ret.std() + 1e-9)
    
    cum_ret = (1 + final_port_ret).cumprod()
    max_dd = ((cum_ret - cum_ret.cummax()) / cum_ret.cummax()).min()
    
    print("========================================================")
    print(f"[*] ORCA: DYNAMIC CORRELATION ALLOCATOR")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    
    spy_r = r['SPY']
    if isinstance(spy_r, pd.DataFrame): spy_r = spy_r.iloc[:, 0]
    bm_cagr = (1 + spy_r).prod() ** (252 / len(spy_r)) - 1
    bm_sharpe = np.sqrt(252) * spy_r.mean() / (spy_r.std() + 1e-9)
    bm_max_dd = (((1 + spy_r).cumprod() - (1 + spy_r).cumprod().cummax()) / (1 + spy_r).cumprod().cummax()).min()
    print(f"[*] SPY BENCHMARK CAGR: {bm_cagr:.2%} | Sharpe: {bm_sharpe:.2f} | Max DD: {bm_max_dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_omni_orca()
