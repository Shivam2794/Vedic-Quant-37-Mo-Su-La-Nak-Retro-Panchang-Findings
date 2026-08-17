import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def run_btc_vol_target():
    print(f"[*] Downloading Data for BTC Vol Target Strategy...")
    df_raw = yf.download(['BTC-USD', '^IRX'], start="2014-01-01", end="2024-01-01", auto_adjust=False)
    
    close_prices = df_raw['Close']['BTC-USD'].dropna()
    open_prices = df_raw['Open']['BTC-USD'].dropna()
    irx = df_raw['Close']['^IRX'].dropna()
    
    # Keep native 365 day for indicator
    sma_fast = close_prices.rolling(10).mean()
    sma_slow = close_prices.rolling(100).mean()
    trend = (sma_fast > sma_slow).astype(float).shift(1).fillna(0.0)
    
    vol20 = close_prices.pct_change().rolling(20).std() * np.sqrt(365)
    # Target 30% annualized vol
    vol_w = (0.15 / vol20).clip(upper=1.5).shift(1).fillna(0.0)
    
    weights = trend * vol_w
    
    # ---------------------------
    # Execute on strict business days
    biz_idx = close_prices[close_prices.index.dayofweek < 5].index
    
    weights_biz = weights.loc[biz_idx]
    
    open_biz = open_prices.loc[biz_idx]
    r_open = (open_biz.shift(-1) / open_biz) - 1
    
    irx = irx.reindex(biz_idx).ffill()
    cy = (irx / 100) / 252
    cy = cy.fillna(0.0001)
    
    valid_idx = biz_idx[250:-1]
    
    w = weights_biz.loc[valid_idx]
    r = r_open.loc[valid_idx]
    c_y = cy.loc[valid_idx]
    
    delta = w.diff().abs().fillna(0)
    slip = delta * 0.0020 # 20 bps slippage
    
    a_ret = w * r
    cash = 1.0 - w.abs()
    
    # Borrow cost
    borrow_cost = c_y + (0.015 / 252)
    c_ret = np.where(cash > 0, cash * c_y, cash * borrow_cost)
    
    final_port_ret = a_ret + c_ret - slip
    
    excess = final_port_ret - c_y
    std = final_port_ret.std()
    
    sharpe = np.sqrt(252) * excess.mean() / std
    cagr = (1 + final_port_ret).prod() ** (252 / len(final_port_ret)) - 1
    cum = (1 + final_port_ret).cumprod()
    max_dd = ((cum - cum.cummax()) / cum.cummax()).min()
    
    print("========================================================")
    print(f"[*] BTC VOL TARGET (10/100 trend, 30% Vol)")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_btc_vol_target()
