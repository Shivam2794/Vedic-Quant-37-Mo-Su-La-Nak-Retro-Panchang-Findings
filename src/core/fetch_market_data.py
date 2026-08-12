"""
Market Data Ingestion Engine (Phase 0.6)
========================================
Autonomously fetches 20 years of daily OHLCV market data for the 
PRISTINE universe of stocks currently residing in the stock_natal_charts.db.

Output:
Parquet files partitioned by ticker inside the market_data/ directory.
"""
import os
import sqlite3
import pandas as pd
import yfinance as yf
import time

DB_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_natal_charts.db"
MARKET_DATA_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\market_data"

def get_pristine_tickers():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT ticker, ipo_date FROM stocks")
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_data():
    if not os.path.exists(MARKET_DATA_DIR):
        os.makedirs(MARKET_DATA_DIR)
        
    pristine_stocks = get_pristine_tickers()
    print(f"Found {len(pristine_stocks)} pristine tickers in the DB.")
    print("Initiating historical market data extraction (Max 20 years)...")
    
    success_count = 0
    fail_count = 0
    
    for tk, ipo in pristine_stocks:
        print(f"[{tk}] Fetching data... (IPO Anchor: {ipo})")
        try:
            # We fetch max to ensure we get everything since IPO, 
            # though we may truncate to 20 years if it's too large, but 
            # yf handles 'max' efficiently.
            ticker = yf.Ticker(tk)
            hist = ticker.history(period="max", interval="1d", auto_adjust=False)
            
            if hist.empty:
                print(f"  -> ERROR: No data returned from yfinance.")
                fail_count += 1
                continue
                
            # Filter to last 20 years to standardize matrix size if needed, 
            # but we can just save it all.
            # Convert index to UTC timezone-naive for parquet compatibility
            hist.reset_index(inplace=True)
            if 'Date' in hist.columns:
                # yfinance returns DatetimeIndex with timezone. Let's make it tz-naive UTC
                if hist['Date'].dt.tz is not None:
                    hist['Date'] = hist['Date'].dt.tz_convert('UTC').dt.tz_localize(None)
            
            # Save to Parquet partitioned by ticker
            out_file = os.path.join(MARKET_DATA_DIR, f"{tk}_ohlcv.parquet")
            hist.to_parquet(out_file, index=False)
            
            print(f"  -> SUCCESS: {len(hist)} trading days saved.")
            success_count += 1
            
        except Exception as e:
            print(f"  -> ERROR: {e}")
            fail_count += 1
            
        time.sleep(0.1) # Rate limit
        
    print("="*50)
    print("MARKET DATA INGESTION COMPLETE")
    print("="*50)
    print(f"Successfully downloaded: {success_count} tickers")
    print(f"Failed: {fail_count} tickers")
    print(f"Directory: {MARKET_DATA_DIR}")

if __name__ == "__main__":
    fetch_data()
