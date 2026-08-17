import yfinance as yf
import pandas as pd
import numpy as np

def compute_drawdown(cum_returns):
    rolling_max = cum_returns.cummax()
    drawdown = (cum_returns - rolling_max) / rolling_max
    return drawdown.min()

def compute_cagr(cum_returns, days):
    total_return = cum_returns.iloc[-1]
    years = days / 252.0
    return (total_return ** (1 / years)) - 1

print("Downloading Data...")
data = yf.download(['QQQ', 'TLT'], start='2005-01-01', end='2026-07-07', auto_adjust=False)['Close'].dropna()

df = pd.DataFrame()
df['QQQ_ret'] = data['QQQ'].pct_change()
df['TLT_ret'] = data['TLT'].pct_change()
df['QQQ_MA200'] = data['QQQ'].rolling(200).mean()

# Daily volatility of QQQ
df['QQQ_vol'] = df['QQQ_ret'].rolling(20).std() * np.sqrt(252)

df = df.dropna()

# Strategy: 1.5x QQQ Trend Following
w_qqq = np.ones(len(df)) * 1.5

# Apply Trend Filter: If QQQ below 200d MA, go to 100% Cash (0% QQQ)
trend_bear = (data['QQQ'].reindex(df.index) < df['QQQ_MA200']).values
w_qqq[trend_bear] = 0.0

w_qqq_series = pd.Series(w_qqq, index=df.index).shift(1).fillna(0)

# Borrowing cost (3% annualized) for leverage > 1
borrow_cost = (w_qqq_series - 1.0).clip(lower=0) * (0.03 / 252)

strat_ret = (w_qqq_series * df['QQQ_ret']) - borrow_cost
cum_returns = (1 + strat_ret).cumprod()

cagr = compute_cagr(cum_returns, len(cum_returns))
mdd = compute_drawdown(cum_returns)

print(f"=== TRUE HOLY GRAIL SOLVER ===")
print(f"CAGR: {cagr*100:.2f}%")
print(f"Max Drawdown: {mdd*100:.2f}%")
