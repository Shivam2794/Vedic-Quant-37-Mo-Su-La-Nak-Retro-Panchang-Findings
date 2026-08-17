import pandas as pd
import numpy as np
import yfinance as yf

# Get data
df = yf.download(['SPY', 'QQQ'], start='1999-01-01', progress=False, auto_adjust=False)['Close']
df = df.ffill().bfill()
rets = df.pct_change().fillna(0)

print("PANDAS NATIVE SHARPE (Buy & Hold)")
spy_sharpe = (rets['SPY'].mean() / rets['SPY'].std()) * np.sqrt(252)
qqq_sharpe = (rets['QQQ'].mean() / rets['QQQ'].std()) * np.sqrt(252)
print(f"SPY: {spy_sharpe:.4f}")
print(f"QQQ: {qqq_sharpe:.4f}")

# Custom Welford test
def welford_sharpe(r_arr):
    mean = 0.0
    m2 = 0.0
    T = len(r_arr)
    # matching the kernel exact logic
    for t in range(1, T):
        r = r_arr[t]
        delta = r - mean
        mean += delta / t
        m2 += delta * (r - mean)
    
    if m2 > 0:
        return (mean / np.sqrt(m2 / (T-2))) * 15.874507866
    return 0.0

print("\nWELFORD KERNEL SHARPE (Buy & Hold)")
spy_w = welford_sharpe(rets['SPY'].values)
qqq_w = welford_sharpe(rets['QQQ'].values)
print(f"SPY: {spy_w:.4f}")
print(f"QQQ: {qqq_w:.4f}")

# Now let's test a random strategy that is in the market 50% of the time, with 5 bps TC
np.random.seed(42)
signals = np.random.randint(0, 2, len(rets))
def strategy_sharpe(r_arr, sigs):
    mean = 0.0
    m2 = 0.0
    T = len(r_arr)
    prev = 0.0
    for t in range(1, T):
        t0 = float(sigs[t])
        r = r_arr[t]
        tc = abs(t0 - prev) * 0.0005
        ra = (r * t0) - tc
        
        delta = ra - mean
        mean += delta / t
        m2 += delta * (ra - mean)
        prev = t0
    
    if m2 > 0:
        return (mean / np.sqrt(m2 / (T-2))) * 15.874507866
    return 0.0

print("\nRANDOM 50% STRATEGY + 5bps TC")
spy_rand = strategy_sharpe(rets['SPY'].values, signals)
print(f"SPY Random: {spy_rand:.4f}")

