"""
Download OHLCV parquet files for the 10 new index/commodity/ETF tickers.
Uses yfinance with the same format as the existing market data files.
"""
import yfinance as yf
import pandas as pd
import os

OUTPUT_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\market_data"

TICKERS_INCEPTION = {
    "SPY":  "1993-01-22",
    "QQQ":  "1999-03-10",
    "IWM":  "2000-05-26",
    "DIA":  "1998-01-20",
    "GLD":  "2004-11-18",
    "SLV":  "2006-04-28",
    "USO":  "2006-04-10",
    "TLT":  "2002-07-26",
    "XLE":  "1998-12-22",
    "VIXY": "2011-01-04",
}

for ticker, inception in TICKERS_INCEPTION.items():
    out_path = os.path.join(OUTPUT_DIR, f"{ticker}_ohlcv.parquet")
    if os.path.exists(out_path):
        print(f"{ticker}: already exists, skipping")
        continue

    print(f"Downloading {ticker} from {inception}...")
    try:
        df = yf.download(ticker, start=inception, end="2025-12-31",
                         interval="1d", auto_adjust=True, progress=False)
        if df.empty:
            print(f"  {ticker}: empty result!")
            continue

        # Flatten MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]

        df = df.reset_index()
        df.columns = [c.strip() for c in df.columns]

        # Standardise column names
        rename = {}
        for col in df.columns:
            cl = col.lower()
            if cl == 'date': rename[col] = 'Date'
            elif cl == 'open': rename[col] = 'Open'
            elif cl == 'high': rename[col] = 'High'
            elif cl == 'low': rename[col] = 'Low'
            elif cl == 'close': rename[col] = 'Close'
            elif cl == 'volume': rename[col] = 'Volume'
        df = df.rename(columns=rename)

        # Ensure Date column is datetime
        df['Date'] = pd.to_datetime(df['Date'])

        # Keep only standard columns
        keep = [c for c in ['Date','Open','High','Low','Close','Volume'] if c in df.columns]
        df = df[keep].dropna(subset=['Date','Close'])

        df.to_parquet(out_path, index=False)
        print(f"  {ticker}: {len(df)} rows saved -> {out_path}")

    except Exception as e:
        print(f"  {ticker}: ERROR — {e}")

print("\nDone.")
