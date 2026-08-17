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

def run_high_winrate_swing():
    print("[*] Downloading Swing Trading Data...")
    df = yf.download('SPY', start="2005-01-01", end="2024-01-01", auto_adjust=False)['Close']
    df = df[~df.index.duplicated(keep='first')]
    df = df.ffill().dropna()
    
    returns = df.pct_change().dropna()
    
    spy = df
    if isinstance(spy, pd.DataFrame): spy = spy.iloc[:, 0]
        
    sma200 = spy.rolling(200).mean()
    sma5 = spy.rolling(5).mean()
    rsi2 = rsi(spy, 2)
    
    # Bollinger Bands (20 day, 2 std dev)
    ma20 = spy.rolling(20).mean()
    std20 = spy.rolling(20).std()
    lower_bb = ma20 - (2 * std20)
    
    weights = pd.Series(0.0, index=df.index)
    
    in_position = False
    
    for i in range(len(df)):
        date = df.index[i]
        
        if pd.isna(sma200.iloc[i]):
            continue
            
        # Exit rule: Close > 5-day SMA
        if in_position and spy.iloc[i] > sma5.iloc[i]:
            in_position = False
            
        # Entry rule: RSI(2) < 5 AND Close < Lower BB AND Close > 200 SMA (Bull Regime)
        if not in_position and spy.iloc[i] < lower_bb.iloc[i] and rsi2.iloc[i] < 5 and spy.iloc[i] > sma200.iloc[i]:
            in_position = True
            
        if in_position:
            weights.loc[date] = 1.0

    # Shift to prevent look-ahead bias
    weights = weights.shift(1).fillna(0.0)
    
    valid_idx = returns.index.intersection(weights.index)[200:]
    weights = weights.loc[valid_idx]
    r = returns.loc[valid_idx]
    if isinstance(r, pd.DataFrame): r = r.iloc[:, 0]
        
    port_ret = weights * r
    
    # Turnover calculation
    delta = weights.diff().abs().fillna(0)
    port_ret -= (delta * SLIPPAGE_BPS)
    
    # We only care about active capital return when evaluating this sub-component, 
    # but to compare to SPY we must include the days sitting in cash
    # Assuming Cash yields 2% annually
    cash_ret = (1.0 - weights) * (0.02 / 252)
    total_ret = port_ret + cash_ret
    
    cagr = (1 + total_ret).prod() ** (252 / len(total_ret)) - 1
    sharpe = np.sqrt(252) * total_ret.mean() / (total_ret.std() + 1e-9)
    
    cum_ret = (1 + total_ret).cumprod()
    max_dd = ((cum_ret - cum_ret.cummax()) / cum_ret.cummax()).min()
    annual_turnover = delta.sum() * 252 / len(total_ret)
    
    print("========================================================")
    print(f"[*] HIGH-WIN-RATE SWING TRADING RESULTS")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    print(f"Annual Turnover: {annual_turnover:.2f}x")
    
    # Benchmark SPY
    bm_cagr = (1 + r).prod() ** (252 / len(r)) - 1
    bm_sharpe = np.sqrt(252) * r.mean() / (r.std() + 1e-9)
    bm_max_dd = (((1 + r).cumprod() - (1 + r).cumprod().cummax()) / (1 + r).cumprod().cummax()).min()
    print(f"[*] SPY BENCHMARK CAGR: {bm_cagr:.2%} | Sharpe: {bm_sharpe:.2f} | Max DD: {bm_max_dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_high_winrate_swing()
