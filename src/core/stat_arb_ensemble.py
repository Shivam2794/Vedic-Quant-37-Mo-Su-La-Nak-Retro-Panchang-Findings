import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def rsi(series, period=2):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=period-1, adjust=False).mean()
    ema_down = down.ewm(com=period-1, adjust=False).mean()
    rs = ema_up / ema_down
    return 100 - (100 / (1 + rs))

def run_stat_arb():
    tickers = ['SPY', 'QQQ', 'TLT', 'GLD', 'LQD', 'HYG', 'VNQ', 'XLE', 'XLF', 'XLK', 'XLV', 'XLU', '^IRX']
    print(f"[*] Downloading Data for {len(tickers)-1} assets...")
    df = yf.download(tickers, start="2010-01-01", end="2024-01-01")['Close']
    df = df[~df.index.duplicated(keep='first')]
    df = df.ffill().dropna()
    df = df[df.index.dayofweek < 5] # Strict business days
    
    returns = df.pct_change().dropna()
    daily_cash_yield = (df['^IRX'] / 100) / 252
    daily_cash_yield = daily_cash_yield.fillna(0.0001)
    
    valid_idx = returns.index[250:]
    
    master_weights = pd.DataFrame(0.0, index=df.index, columns=tickers)
    
    # Run Larry Connors RSI(2) mean reversion on all assets
    for t in tickers:
        if t == '^IRX': continue
        
        asset = df[t]
        sma200 = asset.rolling(200).mean()
        sma5 = asset.rolling(5).mean()
        r2 = rsi(asset, 2)
        
        # Bollinger Bands
        ma20 = asset.rolling(20).mean()
        std20 = asset.rolling(20).std()
        lower_bb = ma20 - (2 * std20)
        
        in_pos = False
        weights = pd.Series(0.0, index=df.index)
        
        for i in range(len(df)):
            date = df.index[i]
            if pd.isna(sma200.iloc[i]): continue
            
            # Exit
            if in_pos and asset.iloc[i] > sma5.iloc[i]:
                in_pos = False
                
            # Entry
            if not in_pos and asset.iloc[i] < lower_bb.iloc[i] and r2.iloc[i] < 10 and asset.iloc[i] > sma200.iloc[i]:
                in_pos = True
                
            if in_pos:
                weights.loc[date] = 1.0 / (len(tickers) - 1) # Equal weight fraction
                
        # SHIFT TO PREVENT LOOKAHEAD BIAS
        master_weights[t] = weights.shift(1).fillna(0.0)
        
    master_weights = master_weights.loc[valid_idx]
    
    # Calculate returns
    r = returns.loc[valid_idx]
    daily_cash_yield = daily_cash_yield.loc[valid_idx]
    
    final_port_ret = pd.Series(0.0, index=valid_idx)
    
    # Better slippage calculation
    delta = master_weights.diff().abs().fillna(0)
    slip_total = delta.drop(columns=['^IRX']).sum(axis=1) * (5 / 10000)
    
    for date in valid_idx:
        w = master_weights.loc[date].drop('^IRX')
        gross = w.abs().sum()
        cash = 1.0 - gross
        
        a_ret = (w * r.loc[date].drop('^IRX')).sum()
        c_ret = cash * daily_cash_yield.loc[date]
            
        final_port_ret.loc[date] = a_ret + c_ret - slip_total.loc[date]
        
    excess_ret = final_port_ret - daily_cash_yield
    cagr = (1 + final_port_ret).prod() ** (252 / len(final_port_ret)) - 1
    sharpe = np.sqrt(252) * excess_ret.mean() / (final_port_ret.std() + 1e-9)
    cum_ret = (1 + final_port_ret).cumprod()
    max_dd = ((cum_ret - cum_ret.cummax()) / cum_ret.cummax()).min()
    
    print("========================================================")
    print(f"[*] CROSS-ASSET MEAN REVERSION ENSEMBLE")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_stat_arb()
