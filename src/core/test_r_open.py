import yfinance as yf
import pandas as pd

tickers = ['SPY', 'BTC-USD']
df_raw = yf.download(tickers, start="2023-10-01", end="2023-10-10")
open_prices = df_raw['Open'].ffill().dropna()

r_open = (open_prices.shift(-1) / open_prices) - 1
biz_idx = open_prices[open_prices.index.dayofweek < 5].index
r_open_biz = r_open.loc[biz_idx]

print("--- Open Prices ---")
print(open_prices)
print("--- r_open ---")
print(r_open)
print("--- r_open_biz (used in strategy) ---")
print(r_open_biz)
