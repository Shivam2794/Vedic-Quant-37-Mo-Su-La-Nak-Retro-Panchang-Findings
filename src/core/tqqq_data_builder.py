import os
import requests
import pandas as pd
import datetime
from tenacity import retry, wait_exponential, stop_after_attempt
from dotenv import load_dotenv

load_dotenv()
ALPACA_API_KEY = os.environ.get("ALPACA_API_KEY")
ALPACA_API_SECRET = os.environ.get("ALPACA_SECRET_KEY")
ALPACA_DATA_URL = "https://data.alpaca.markets/v2"

headers = {
    "APCA-API-KEY-ID": ALPACA_API_KEY,
    "APCA-API-SECRET-KEY": ALPACA_API_SECRET,
    "accept": "application/json"
}

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(5))
def fetch_bars_paginated(symbol, timeframe, start_date, end_date):
    print(f"Fetching {symbol} {timeframe} data from {start_date} to {end_date}...")
    all_bars = []
    page_token = None
    
    while True:
        params = {
            "timeframe": timeframe,
            "start": start_date,
            "end": end_date,
            "limit": 10000
        }
        if page_token:
            params["page_token"] = page_token
            
        res = requests.get(f"{ALPACA_DATA_URL}/stocks/{symbol}/bars", headers=headers, params=params)
        res.raise_for_status()
        data = res.json()
        
        bars = data.get('bars', [])
        if bars:
            all_bars.extend(bars)
            
        page_token = data.get('next_page_token')
        if not page_token:
            break
            
    if not all_bars:
        return pd.DataFrame()
        
    df = pd.DataFrame(all_bars)
    df.rename(columns={'t': 'timestamp', 'o': 'Open', 'h': 'High', 'l': 'Low', 'c': 'Close', 'v': 'Volume'}, inplace=True)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def build_dataset():
    start = "2021-01-01T00:00:00Z"
    end = "2023-12-31T23:59:59Z"
    
    # 1. Fetch Daily QQQ for features
    qqq_daily = fetch_bars_paginated('QQQ', '1Day', start, end)
    qqq_daily.set_index('timestamp', inplace=True)
    
    # 2. Fetch 1-Min QQQ for First Hour logic
    qqq_1m = fetch_bars_paginated('QQQ', '1Min', start, end)
    qqq_1m.set_index('timestamp', inplace=True)
    
    # 3. Fetch 1-Min TQQQ for Intraday High/Low/Close simulation
    tqqq_1m = fetch_bars_paginated('TQQQ', '1Min', start, end)
    tqqq_1m.set_index('timestamp', inplace=True)
    
    qqq_daily.to_parquet("qqq_daily.parquet")
    qqq_1m.to_parquet("qqq_1m.parquet")
    tqqq_1m.to_parquet("tqqq_1m.parquet")
    print("Saved all historical data to parquets.")

if __name__ == "__main__":
    build_dataset()
