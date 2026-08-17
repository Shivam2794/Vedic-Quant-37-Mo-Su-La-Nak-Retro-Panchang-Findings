import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def run_overnight_drift():
    print(f"[*] Downloading Data for Overnight Drift Strategy...")
    df_raw = yf.download(['SPY', '^IRX'], start="2000-01-01", end="2024-01-01", auto_adjust=False)
    
    close_prices = df_raw['Close']['SPY'].dropna()
    open_prices = df_raw['Open']['SPY'].dropna()
    irx = df_raw['Close']['^IRX'].dropna()
    
    biz_idx = close_prices[close_prices.index.dayofweek < 5].index
    
    close_prices = close_prices.loc[biz_idx]
    open_prices = open_prices.loc[biz_idx]
    irx = irx.reindex(biz_idx).ffill()
    cy = (irx / 100) / 252
    cy = cy.fillna(0.0001)
    
    valid_idx = biz_idx[:-1]
    
    # Return from Close(T) to Open(T+1)
    # Open(T+1) is open_prices.shift(-1)
    overnight_ret = (open_prices.shift(-1) / close_prices) - 1
    overnight_ret = overnight_ret.loc[valid_idx]
    
    # Intraday Return: Open(T) to Close(T)
    intraday_ret = (close_prices / open_prices) - 1
    intraday_ret = intraday_ret.loc[valid_idx]
    
    # Strategy: Always hold overnight.
    # We enter at Close(T), exit at Open(T+1).
    # Slippage: 2bps on entry, 2bps on exit = 4bps total per day
    slip = 0.0004
    
    # We hold 100% SPY overnight, 0% intraday
    final_port_ret = overnight_ret - slip
    
    # During the day we hold cash
    c_ret = cy.loc[valid_idx]
    final_port_ret = final_port_ret + c_ret
    
    excess = final_port_ret - cy.loc[valid_idx]
    std = final_port_ret.std()
    
    sharpe = np.sqrt(252) * excess.mean() / std
    cagr = (1 + final_port_ret).prod() ** (252 / len(final_port_ret)) - 1
    cum = (1 + final_port_ret).cumprod()
    max_dd = ((cum - cum.cummax()) / cum.cummax()).min()
    
    print("========================================================")
    print(f"[*] SPY OVERNIGHT DRIFT")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    print("========================================================")
    
    # Baseline SPY
    spy_ret = close_prices.pct_change().loc[valid_idx]
    spy_excess = spy_ret - cy.loc[valid_idx]
    spy_sharpe = np.sqrt(252) * spy_excess.mean() / spy_ret.std()
    spy_cagr = (1 + spy_ret).prod() ** (252 / len(spy_ret)) - 1
    print(f"[*] SPY BUY & HOLD")
    print(f"CAGR: {spy_cagr:.2%}")
    print(f"Sharpe: {spy_sharpe:.2f}")
    print("========================================================")

if __name__ == "__main__":
    run_overnight_drift()
