import yfinance as yf
tickers = ["DBC", "^SPGSCI", "^BCOM", "CL=F", "GC=F"]
for t in tickers:
    df = yf.download(t, start="2000-01-01", end="2024-01-01", progress=False)
    print(f"{t}: {len(df)} rows, starts {df.index.min() if not df.empty else 'EMPTY'}")
