import os
import pandas as pd
import numpy as np
import glob

MARKET_DATA_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\market_data"
OUTPUT_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_returns.parquet"

def generate_returns():
    print("Generating stock returns for all tickers...")
    files = glob.glob(os.path.join(MARKET_DATA_DIR, "*_ohlcv.parquet"))
    
    all_dfs = []
    
    for f in files:
        ticker = os.path.basename(f).split('_')[0]
        df = pd.read_parquet(f)
        
        # Ensure we have required columns
        if 'Date' not in df.columns or 'Close' not in df.columns:
            continue
            
        # Compute forward returns
        df['fwd_return_1d'] = df['Close'].pct_change(periods=1).shift(-1)
        df['fwd_return_5d'] = df['Close'].pct_change(periods=5).shift(-5)
        df['fwd_return_10d'] = df['Close'].pct_change(periods=10).shift(-10)
        df['fwd_return_21d'] = df['Close'].pct_change(periods=21).shift(-21)
        df['fwd_return_63d'] = df['Close'].pct_change(periods=63).shift(-63)
        
        # Format for BigQuery
        # df['Date'] is already timezone-aware or naive. Let's ensure it's UTC timestamp.
        df['date'] = pd.to_datetime(df['Date'], utc=True)
        df['ticker'] = ticker
        df['close'] = df['Close']
        
        df_out = df[['date', 'close', 'ticker', 'fwd_return_1d', 'fwd_return_5d', 'fwd_return_10d', 'fwd_return_21d', 'fwd_return_63d']]
        all_dfs.append(df_out)
        
    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df = final_df.dropna(subset=['fwd_return_1d']) # Drop rows where we can't even compute 1D return
    final_df.to_parquet(OUTPUT_PATH, index=False)
    print(f"Generated {len(final_df)} rows for {len(all_dfs)} tickers. Saved to {OUTPUT_PATH}")

if __name__ == '__main__':
    generate_returns()
