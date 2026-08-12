import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

SLIPPAGE_BPS = 10 / 10000

def run_leveraged_sector_momentum():
    print("[*] Downloading Leveraged Sector Data...")
    # TECL (Tech 3x), FAS (Financials 3x), SOXL (Semis 3x), TNA (Small Cap 3x), SHV (Cash)
    tickers = ['TECL', 'FAS', 'SOXL', 'TNA', 'SHV']
    
    # SOXL inception is 2010
    df = yf.download(tickers, start="2011-01-01", end="2024-01-01")['Close']
    df = df[~df.index.duplicated(keep='first')]
    df = df.ffill().dropna()
    
    returns = df.pct_change().dropna()
    
    # 3-Month Momentum for highly reactive rotation
    mom3 = df.pct_change(63)
    
    # 200-day SMA of SPY as a strict macro filter
    spy = yf.download('SPY', start="2010-01-01", end="2024-01-01")['Close']
    spy = spy[~spy.index.duplicated(keep='first')]
    spy = spy.ffill().dropna()
    spy_sma = spy.rolling(200).mean()
    
    # Trailing Stop mechanism
    # If the portfolio drops 10% from its localized peak, immediately move to Cash until next month.
    
    df['YearMonth'] = df.index.to_period('M')
    month_ends = df.groupby('YearMonth').tail(1).index
    
    assets = ['TECL', 'FAS', 'SOXL', 'TNA']
    weights = pd.DataFrame(0.0, index=df.index, columns=tickers)
    
    current_asset = 'SHV'
    
    for date in month_ends:
        if date not in mom3.index or date not in spy_sma.index:
            continue
            
        spy_val = spy.loc[date]
        if isinstance(spy_val, pd.Series): spy_val = spy_val.iloc[0]
            
        sma_val = spy_sma.loc[date]
        if isinstance(sma_val, pd.Series): sma_val = sma_val.iloc[0]
            
        if pd.isna(sma_val) or pd.isna(spy_val):
            continue
            
        is_bull_regime = spy_val > sma_val
            
        if not is_bull_regime:
            current_asset = 'SHV'
            weights.loc[date, current_asset] = 1.0
            continue
            
        # Get momentum scores
        scores = mom3.loc[date, assets]
        if isinstance(scores, pd.DataFrame): scores = scores.iloc[0]
            
        # Must be positive to even consider
        if (scores > 0).any():
            current_asset = scores.idxmax()
            weights.loc[date, current_asset] = 1.0
        else:
            current_asset = 'SHV'
            weights.loc[date, current_asset] = 1.0

    # Shift by 1 to prevent look-ahead bias
    weights = weights.ffill().shift(1).fillna(0.0)
    
    # Implement Daily Trailing Stop (15% on 3x leveraged is conservative)
    # If daily portfolio value drops 15% from its trailing 20-day high, we wipe weights to SHV
    
    valid_idx = returns.index.intersection(weights.index)[200:]
    weights = weights.loc[valid_idx]
    r = returns.loc[valid_idx]
    
    # Simulating the portfolio day by day to calculate trailing stops accurately
    port_ret = pd.Series(0.0, index=valid_idx)
    daily_weights = weights.copy()
    
    peak = 1.0
    val = 1.0
    stopped_out = False
    stop_month = None
    
    for i in range(1, len(valid_idx)):
        date = valid_idx[i]
        prev_date = valid_idx[i-1]
        
        # Reset stop-out at the start of a new month
        if date.month != prev_date.month:
            stopped_out = False
            peak = val # Reset peak on new rebalance
            
        if stopped_out:
            # Force weight to SHV
            daily_weights.loc[date] = 0.0
            daily_weights.loc[date, 'SHV'] = 1.0
            
        # Calculate today's return based on (potentially overridden) weights
        today_w = daily_weights.loc[date]
        today_r = r.loc[date]
        if isinstance(today_r, pd.DataFrame): today_r = today_r.iloc[0]
        
        day_ret = (today_w * today_r).sum()
        
        # Add SHV yield if in SHV
        if today_w['SHV'] > 0:
            day_ret += today_w['SHV'] * (0.02 / 252)
            
        val *= (1 + day_ret)
        port_ret.loc[date] = day_ret
        
        if val > peak:
            peak = val
            
        # Check stop loss (15% trailing stop)
        if not stopped_out and (peak - val) / peak > 0.15:
            stopped_out = True
            
    # Recalculate turnover with the intra-month stop outs
    delta = daily_weights.diff().abs().sum(axis=1).fillna(0)
    port_ret -= (delta * SLIPPAGE_BPS)
    
    cagr = (1 + port_ret).prod() ** (252 / len(port_ret)) - 1
    sharpe = np.sqrt(252) * port_ret.mean() / (port_ret.std() + 1e-9)
    
    cum_ret = (1 + port_ret).cumprod()
    max_dd = ((cum_ret - cum_ret.cummax()) / cum_ret.cummax()).min()
    annual_turnover = delta.sum() * 252 / len(port_ret)
    
    print("========================================================")
    print(f"[*] LEVERAGED SECTOR MOMENTUM (W/ TRAILING STOP) RESULTS")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    print(f"Annual Turnover: {annual_turnover:.2f}x")
    
    # Benchmark SPY
    spy_ret = yf.download('SPY', start="2011-01-01", end="2024-01-01")['Close'].pct_change().dropna()
    spy_ret = spy_ret.loc[valid_idx]
    if isinstance(spy_ret, pd.DataFrame): spy_ret = spy_ret.iloc[:, 0]
    bm_cagr = (1 + spy_ret).prod() ** (252 / len(spy_ret)) - 1
    bm_sharpe = np.sqrt(252) * spy_ret.mean() / (spy_ret.std() + 1e-9)
    bm_max_dd = (((1 + spy_ret).cumprod() - (1 + spy_ret).cumprod().cummax()) / (1 + spy_ret).cumprod().cummax()).min()
    print(f"[*] SPY BENCHMARK CAGR: {bm_cagr:.2%} | Sharpe: {bm_sharpe:.2f} | Max DD: {bm_max_dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_leveraged_sector_momentum()
