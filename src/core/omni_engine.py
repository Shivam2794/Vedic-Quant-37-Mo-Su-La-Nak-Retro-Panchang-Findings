import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

SLIPPAGE_BPS = 10 / 10000

def run_vol_targeted_hedgefundie():
    print("[*] Downloading Leveraged Universe Data...")
    tickers = ['UPRO', 'TMF', 'SHV']
    # UPRO 2009-06, TMF 2009-04
    df = yf.download(tickers, start="2010-01-01", end="2024-01-01", auto_adjust=False)['Close']
    df = df[~df.index.duplicated(keep='first')]
    df = df.ffill().dropna()
    
    returns = df.pct_change().dropna()
    
    # Base portfolio: 55% UPRO, 45% TMF
    base_ret = returns['UPRO'] * 0.55 + returns['TMF'] * 0.45
    
    # 20-day annualized volatility of the base portfolio
    vol20 = base_ret.rolling(20).std() * np.sqrt(252)
    
    TARGET_VOL = 0.20 # 20% volatility
    
    df['YearMonth'] = df.index.to_period('M')
    month_ends = df.groupby('YearMonth').tail(1).index
    
    weights = pd.DataFrame(np.nan, index=df.index, columns=tickers)
    
    for date in month_ends:
        if date not in vol20.index:
            continue
            
        current_vol = vol20.loc[date]
        if isinstance(current_vol, pd.Series):
            current_vol = current_vol.iloc[0]
            
        if pd.isna(current_vol) or current_vol == 0:
            continue
            
        multiplier = TARGET_VOL / current_vol
        multiplier = min(multiplier, 1.0) # Cap at 1.0 (no margin)
        
        weights.loc[date, 'UPRO'] = 0.55 * multiplier
        weights.loc[date, 'TMF'] = 0.45 * multiplier
        weights.loc[date, 'SHV'] = 1.0 - multiplier

    # Shift by 1 to prevent look-ahead bias
    weights = weights.ffill().shift(1).fillna(0.0)
    
    valid_idx = returns.index.intersection(weights.index)[20:]
    weights = weights.loc[valid_idx]
    r = returns.loc[valid_idx]
    
    port_ret = (weights['UPRO'] * r['UPRO']) + (weights['TMF'] * r['TMF']) + (weights['SHV'] * r['SHV'])
    
    # Turnover calculation
    delta = pd.Series(0.0, index=weights.index)
    rebalance_dates = [d for d in month_ends if d in weights.index]
    for i in range(1, len(rebalance_dates)):
        curr = rebalance_dates[i]
        prev = rebalance_dates[i-1]
        delta.loc[curr] = (weights.loc[curr] - weights.loc[prev]).abs().sum()
        
    port_ret -= (delta * SLIPPAGE_BPS)
    
    cagr = (1 + port_ret).prod() ** (252 / len(port_ret)) - 1
    sharpe = np.sqrt(252) * port_ret.mean() / (port_ret.std() + 1e-9)
    
    cum_ret = (1 + port_ret).cumprod()
    max_dd = ((cum_ret - cum_ret.cummax()) / cum_ret.cummax()).min()
    annual_turnover = delta.sum() * 252 / len(port_ret)
    
    print("========================================================")
    print(f"[*] VOLATILITY-TARGETED HEDGEFUNDIE RESULTS")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    print(f"Annual Turnover: {annual_turnover:.2f}x")
    
    # Benchmark SPY
    spy = yf.download('SPY', start="2010-01-01", end="2024-01-01", auto_adjust=False)['Close'].pct_change().dropna()
    spy = spy.loc[valid_idx]
    bm_cagr = (1 + spy).prod() ** (252 / len(spy)) - 1
    bm_sharpe = np.sqrt(252) * spy.mean() / (spy.std() + 1e-9)
    bm_max_dd = (((1 + spy).cumprod() - (1 + spy).cumprod().cummax()) / (1 + spy).cumprod().cummax()).min()
    print(f"[*] SPY BENCHMARK CAGR: {bm_cagr:.2%} | Sharpe: {bm_sharpe:.2f} | Max DD: {bm_max_dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_vol_targeted_hedgefundie()
