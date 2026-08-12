import os
import gc
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

def get_alpaca_client():
    load_dotenv(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\.env")
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    if not api_key or not secret_key:
        raise ValueError("Missing ALPACA_API_KEY or ALPACA_SECRET_KEY in .env")
    return StockHistoricalDataClient(api_key, secret_key)

def fetch_data_in_chunks(client, symbol, start_date, end_date):
    """
    Fetch data month by month to avoid timeouts or memory explosions.
    """
    all_dfs = []
    current_start = start_date
    
    print(f"\n--- Downloading {symbol} from {start_date.date()} to {end_date.date()} ---")
    while current_start < end_date:
        current_end = min(current_start + relativedelta(months=1), end_date)
        print(f"  Fetching: {current_start.date()} to {current_end.date()}...", end=" ", flush=True)
        
        req = StockBarsRequest(
            symbol_or_symbols=[symbol],
            timeframe=TimeFrame.Minute,
            start=current_start,
            end=current_end
        )
        
        try:
            bars = client.get_stock_bars(req)
            if bars.df.empty:
                print("No data.")
            else:
                df = bars.df.reset_index()
                # Drop symbol column
                if 'symbol' in df.columns:
                    df = df.drop(columns=['symbol'])
                
                print(f"Found {len(df)} rows.")
                all_dfs.append(df)
        except Exception as e:
            if "not found" in str(e).lower() or "no data" in str(e).lower() or "not found" in str(e):
                print(f"No data returned.")
            else:
                print(f"Error: {e}")
                
        current_start = current_end
        
    if not all_dfs:
        print(f"No data downloaded at all for {symbol}.")
        return None
        
    combined = pd.concat(all_dfs, ignore_index=True)
    
    # Clean up
    combined = combined.rename(columns={
        'timestamp': 'Date',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume',
        'vwap': 'VWAP',
        'trade_count': 'Trade_Count'
    })
    
    # Alpaca returns UTC timestamps. We will convert to US/Eastern to match existing V12 engine.
    combined['Date'] = pd.to_datetime(combined['Date'])
    combined['Date'] = combined['Date'].dt.tz_convert('US/Eastern')
    combined = combined.set_index('Date')
    
    # Keep only standard OHLCV
    cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    combined = combined[cols]
    
    # Drop duplicates just in case
    combined = combined[~combined.index.duplicated(keep='last')]
    combined = combined.sort_index()
    
    return combined

if __name__ == "__main__":
    client = get_alpaca_client()
    
    start_dt = datetime(2016, 7, 1)
    end_dt = datetime(2026, 7, 27)
    
    out_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
    
    for symbol in ["QQQ", "TQQQ"]:
        df = fetch_data_in_chunks(client, symbol, start_dt, end_dt)
        if df is not None:
            out_file = os.path.join(out_dir, f"{symbol.lower()}_1m.parquet")
            print(f"Saving {symbol} ({len(df)} rows) to {out_file}...")
            df.to_parquet(out_file)
            print("Done.")
            del df
            gc.collect()
            
    print("\nALL DATA SUCCESSFULLY DOWNLOADED AND ALIGNED!")
