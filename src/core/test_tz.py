import pandas as pd
import yfinance as yf
df = yf.download("SPY", start="2014-01-01", end="2024-01-01", progress=False)
valid_idx = df.index
try:
    mask = valid_idx < pd.Timestamp("2018-01-01")
    print("Success")
except Exception as e:
    print("Error:", type(e), e)
