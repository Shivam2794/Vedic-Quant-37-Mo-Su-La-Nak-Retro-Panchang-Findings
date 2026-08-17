import pandas as pd
import yfinance as yf
df = yf.download("SPY", start="2014-01-01", end="2024-01-01", progress=False, auto_adjust=False)
try:
    print(df.index.tz)
    sl = df.loc["2014-01-01":"2017-12-31"]
    print("Slicing worked, len:", len(sl))
except Exception as e:
    print("Slicing error:", type(e), e)
