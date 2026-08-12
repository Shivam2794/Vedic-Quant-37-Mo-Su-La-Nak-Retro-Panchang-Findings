import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

SLIPPAGE_BPS = 10 / 10000

def rsi(series, period=2):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=period-1, adjust=False).mean()
    ema_down = down.ewm(com=period-1, adjust=False).mean()
    rs = ema_up / ema_down
    return 100 - (100 / (1 + rs))

def run_connors_rsi2():
    print("[*] Downloading SPY & TLT Data...")
    df = yf.download(['SPY', 'TLT'], start="2005-01-01", end="2024-01-01")['Close']
    df = df[~df.index.duplicated(keep='first')]
    df = df.ffill().dropna()
    
    returns = df.pct_change().dropna()
    
    spy = df['SPY']
    sma200 = spy.rolling(200).mean()
    sma5 = spy.rolling(5).mean()
    rsi2 = rsi(spy, 2)
    
    weights = pd.DataFrame(0.0, index=df.index, columns=['SPY', 'TLT'])
    
    in_spy = False
    
    for i in range(len(df)):
        date = df.index[i]
        
        # Don't trade if indicators aren't ready
        if pd.isna(sma200.iloc[i]):
            continue
            
        # Exit rule
        if in_spy and spy.iloc[i] > sma5.iloc[i]:
            in_spy = False
            
        # Entry rule
        if not in_spy and spy.iloc[i] > sma200.iloc[i] and rsi2.iloc[i] < 10:
            in_spy = True
            
        # Allocation
        if in_spy:
            weights.loc[date, 'SPY'] = 1.0
        else:
            # If not in SPY, hold TLT as safe haven
            weights.loc[date, 'TLT'] = 1.0
            
    # Shift to prevent look-ahead
    weights = weights.shift(1).fillna(0.0)
    
    valid_idx = returns.index.intersection(weights.index)[200:]
    weights = weights.loc[valid_idx]
    r = returns.loc[valid_idx]
    
    port_ret = (weights * r).sum(axis=1)
    
    # Turnover calculation (daily)
    delta = weights.diff().abs().sum(axis=1).fillna(0)
    port_ret -= (delta * SLIPPAGE_BPS)
    
    cagr = (1 + port_ret).prod() ** (252 / len(port_ret)) - 1
    sharpe = np.sqrt(252) * port_ret.mean() / (port_ret.std() + 1e-9)
    
    cum_ret = (1 + port_ret).cumprod()
    max_dd = ((cum_ret - cum_ret.cummax()) / cum_ret.cummax()).min()
    annual_turnover = delta.sum() * 252 / len(port_ret)
    
    print("========================================================")
    print(f"[*] LARRY CONNORS RSI-2 RESULTS")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    print(f"Annual Turnover: {annual_turnover:.2f}x")
    
    # Benchmark SPY
    spy_ret = r['SPY']
    bm_cagr = (1 + spy_ret).prod() ** (252 / len(spy_ret)) - 1
    bm_sharpe = np.sqrt(252) * spy_ret.mean() / (spy_ret.std() + 1e-9)
    bm_max_dd = (((1 + spy_ret).cumprod() - (1 + spy_ret).cumprod().cummax()) / (1 + spy_ret).cumprod().cummax()).min()
    print(f"[*] SPY BENCHMARK CAGR: {bm_cagr:.2%} | Sharpe: {bm_sharpe:.2f} | Max DD: {bm_max_dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_connors_rsi2()
