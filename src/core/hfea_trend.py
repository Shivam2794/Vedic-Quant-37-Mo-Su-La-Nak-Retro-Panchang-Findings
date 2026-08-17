import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def run_hfea_trend():
    tickers = ['UPRO', 'TMF', 'SPY', 'TLT', '^IRX']
    print(f"[*] Downloading Data for HFEA Trend...")
    # TQQQ, UPRO, TMF started around 2010. Let's use 2011 to be safe.
    df = yf.download(tickers, start="2011-01-01", end="2024-01-01", auto_adjust=False)['Close']
    df = df[~df.index.duplicated(keep='first')]
    df = df.ffill().dropna()
    df = df[df.index.dayofweek < 5] # Strict business days
    
    returns = df.pct_change().dropna()
    daily_cash_yield = (df['^IRX'] / 100) / 252
    daily_cash_yield = daily_cash_yield.fillna(0.0001)
    
    valid_idx = returns.index[200:]
    
    # Base asset trends (we calculate trend on the underlying un-levered ETF to avoid decay noise)
    spy_sma200 = df['SPY'].rolling(200).mean()
    tlt_sma200 = df['TLT'].rolling(200).mean()
    
    spy_trend = (df['SPY'] > spy_sma200).astype(float).shift(1).fillna(0.0)
    tlt_trend = (df['TLT'] > tlt_sma200).astype(float).shift(1).fillna(0.0)
    
    master_weights = pd.DataFrame(0.0, index=df.index, columns=['UPRO', 'TMF'])
    
    # Base HFEA weights: 55% UPRO, 45% TMF
    # Only hold if the underlying is in an uptrend.
    master_weights['UPRO'] = spy_trend * 0.55
    master_weights['TMF'] = tlt_trend * 0.45
    
    master_weights = master_weights.loc[valid_idx]
    
    r = returns.loc[valid_idx]
    daily_cash_yield = daily_cash_yield.loc[valid_idx]
    
    final_port_ret = pd.Series(0.0, index=valid_idx)
    
    delta = master_weights.diff().abs().fillna(0)
    slip_upro = delta['UPRO'] * (10 / 10000) # 10bps slippage for leveraged ETFs
    slip_tmf = delta['TMF'] * (10 / 10000)
    total_slippage = slip_upro + slip_tmf
    
    for date in valid_idx:
        w = master_weights.loc[date]
        gross = w.abs().sum()
        cash = 1.0 - gross
        
        # We don't borrow here, because the leverage is internal to the ETF. 
        # The ETF pays the borrow cost internally (which is reflected in its price decay).
        # We are simply allocating our cash to the ETF.
        a_ret = (w * r.loc[date][['UPRO', 'TMF']]).sum()
        c_ret = cash * daily_cash_yield.loc[date]
            
        final_port_ret.loc[date] = a_ret + c_ret - total_slippage.loc[date]
        
    excess_ret = final_port_ret - daily_cash_yield
    cagr = (1 + final_port_ret).prod() ** (252 / len(final_port_ret)) - 1
    sharpe = np.sqrt(252) * excess_ret.mean() / (final_port_ret.std() + 1e-9)
    cum_ret = (1 + final_port_ret).cumprod()
    max_dd = ((cum_ret - cum_ret.cummax()) / cum_ret.cummax()).min()
    
    print("========================================================")
    print(f"[*] LEVERAGED ETF TREND (UPRO/TMF)")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_hfea_trend()
