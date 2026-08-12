import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def run_btc_trend():
    print(f"[*] Downloading Data for BTC...")
    df = yf.download(['BTC-USD', '^IRX'], start="2014-01-01", end="2024-01-01")['Close']
    df = df.ffill().dropna()
    df = df[df.index.dayofweek < 5] # Strict business days
    
    returns = df.pct_change().dropna()
    daily_cash_yield = (df['^IRX'] / 100) / 252
    daily_cash_yield = daily_cash_yield.fillna(0.0001)
    
    valid_idx = returns.index[200:]
    
    btc = df['BTC-USD']
    sma50 = btc.rolling(50).mean()
    sma200 = btc.rolling(200).mean()
    
    # Golden cross trend filter
    trend = (sma50 > sma200).astype(float).shift(1).fillna(0.0)
    
    master_weights = pd.DataFrame(0.0, index=df.index, columns=['BTC-USD'])
    master_weights['BTC-USD'] = trend
    
    master_weights = master_weights.loc[valid_idx]
    
    r = returns.loc[valid_idx]
    daily_cash_yield = daily_cash_yield.loc[valid_idx]
    
    final_port_ret = pd.Series(0.0, index=valid_idx)
    
    delta = master_weights.diff().abs().fillna(0)
    slip_btc = delta['BTC-USD'] * (30 / 10000) # 30bps slippage
    
    for date in valid_idx:
        w = master_weights.loc[date]
        gross = w.abs().sum()
        cash = 1.0 - gross
        
        a_ret = (w * r.loc[date][['BTC-USD']]).sum()
        c_ret = cash * daily_cash_yield.loc[date]
            
        final_port_ret.loc[date] = a_ret + c_ret - slip_btc.loc[date]
        
    excess_ret = final_port_ret - daily_cash_yield
    cagr = (1 + final_port_ret).prod() ** (252 / len(final_port_ret)) - 1
    sharpe = np.sqrt(252) * excess_ret.mean() / (final_port_ret.std() + 1e-9)
    cum_ret = (1 + final_port_ret).cumprod()
    max_dd = ((cum_ret - cum_ret.cummax()) / cum_ret.cummax()).min()
    
    print("========================================================")
    print(f"[*] BTC-USD TREND")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_btc_trend()
