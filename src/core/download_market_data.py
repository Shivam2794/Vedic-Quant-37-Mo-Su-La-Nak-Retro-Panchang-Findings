"""
Phase 6A Step 3: Download Market Data + Generate Feature Matrices
=================================================================
Downloads OHLCV market data for all new tickers via yfinance,
then generates the feature matrix using the existing pipeline.

Processes in small batches (5 tickers at a time) to avoid OOM.
"""
import yfinance as yf
import pandas as pd
import os
import time
import gc

MARKET_DATA_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\market_data"

NEW_TICKERS = [
    "TSM", "AMD", "ASML", "INTC", "ADI", "NXPI", "MU",
    "PLTR", "HUBS", "TYL", "TRMB",
    "IBM", "CTSH", "EPAM", "DXC",
    "MTCH", "TRIP", "YELP", "IAC",
    "VZ", "T", "CMCSA", "TMUS",
    "BABA", "MELI", "EBAY", "ETSY", "M", "KSS", "DDS",
    "DG", "KR", "CASY", "BJ",
    "SQ", "FI", "FIS", "JKHY",
    "MCO", "MSCI", "CBOE", "FDS", "LPLA", "EVR",
    "GE", "RTX", "BA", "LMT", "GD", "TDG", "LHX", "AXON",
    "CAT", "CMI", "PCAR", "OSK", "WAB", "TTC", "TEX", "ALSN",
    "AGCO",
    "CSX", "JBHT", "SAIA", "R", "LSTR",
    "UPS", "FDX",
    "JNJ", "ABT",
    "XOM", "CVX",
    "CSGP", "CBRE",
    "APP", "HOOD", "HWM", "CPNG", "TOST", "AFRM", "GO", "CPAY",
    "DOX", "SNDR", "ARCB", "CARG",
]

# yfinance symbol overrides for problematic tickers
SYMBOL_MAP = {
    "SQ": "XYZ",   # Block Inc renamed ticker
    "FI": "FISV",  # Fiserv
}

def download_market_data():
    print("=" * 60, flush=True)
    print("STEP 1: DOWNLOADING MARKET DATA FOR NEW TICKERS", flush=True)
    print("=" * 60, flush=True)
    
    downloaded = 0
    skipped = 0
    failed = []
    
    for i, ticker in enumerate(NEW_TICKERS):
        outpath = os.path.join(MARKET_DATA_DIR, f"{ticker}_ohlcv.parquet")
        
        if os.path.exists(outpath):
            skipped += 1
            continue
        
        symbol = SYMBOL_MAP.get(ticker, ticker)
        print(f"  [{i+1}/{len(NEW_TICKERS)}] Downloading {ticker} (symbol={symbol})...", end=" ", flush=True)
        
        try:
            df = yf.download(symbol, period="max", progress=False, auto_adjust=True)
            if len(df) < 100:
                print(f"SKIP (only {len(df)} rows)", flush=True)
                failed.append(ticker)
                continue
            
            # Normalize columns
            df = df.reset_index()
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [c[0] if c[1] == '' or c[1] == symbol else c[0] for c in df.columns]
            
            # Ensure standard column names
            col_map = {}
            for c in df.columns:
                cl = c.lower()
                if 'date' in cl: col_map[c] = 'Date'
                elif 'open' in cl: col_map[c] = 'Open'
                elif 'high' in cl: col_map[c] = 'High'
                elif 'low' in cl: col_map[c] = 'Low'
                elif 'close' in cl: col_map[c] = 'Close'
                elif 'volume' in cl: col_map[c] = 'Volume'
            df = df.rename(columns=col_map)
            
            df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
            df.to_parquet(outpath, index=False)
            downloaded += 1
            print(f"OK ({len(df)} days)", flush=True)
            
        except Exception as e:
            print(f"ERROR: {e}", flush=True)
            failed.append(ticker)
        
        time.sleep(0.2)
        
        if (i + 1) % 20 == 0:
            gc.collect()
    
    print(f"\nDownloaded: {downloaded}, Skipped (exists): {skipped}, Failed: {len(failed)}", flush=True)
    if failed:
        print(f"Failed tickers: {failed}", flush=True)
    return failed

if __name__ == "__main__":
    failed = download_market_data()
    
    # Verify final count
    files = [f for f in os.listdir(MARKET_DATA_DIR) if f.endswith('.parquet')]
    print(f"\nTotal market data files: {len(files)}", flush=True)
