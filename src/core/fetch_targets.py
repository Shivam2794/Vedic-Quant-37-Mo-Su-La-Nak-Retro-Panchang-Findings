import pandas as pd
import yfinance as yf
import numpy as np

def fetch_and_merge():
    print("Loading features...")
    df = pd.read_csv("ml_features.csv")
    
    df['Transit_Date'] = pd.to_datetime(df['Transit_Date'])
    
    unique_tickers = df['Ticker'].unique()
    print(f"Tickers to fetch: {list(unique_tickers)}")
    
    # We will fetch data from 1999 to 2026 to cover all snapshots
    # To save time and API calls, we download the massive dataframe once
    print("Downloading YF data...")
    yf_data = yf.download(list(unique_tickers), start="1999-01-01", end="2026-12-31", progress=False)
    
    # yfinance returns a multi-index column df if multiple tickers are passed
    # columns are (PriceType, Ticker). We want 'Adj Close'
    adj_close = yf_data['Adj Close'] if 'Adj Close' in yf_data else yf_data['Close']
    
    # Ensure index is timezone-naive to match our parsed dates
    adj_close.index = adj_close.index.tz_localize(None)
    
    # Prepare lists to hold target variables
    targets_10d = []
    targets_direction = []
    
    print("Merging targets...")
    for idx, row in df.iterrows():
        ticker = row['Ticker']
        t_date = row['Transit_Date'].replace(tzinfo=None)
        
        # Get the closing price on the transit date (or the next available trading day)
        # Using bfill (backward fill) to get the next valid trading day if weekend
        try:
            future_prices = adj_close[ticker].loc[t_date:]
            if len(future_prices) == 0:
                targets_10d.append(np.nan)
                targets_direction.append(np.nan)
                continue
                
            # The exact day price (or next valid)
            price_t0 = future_prices.iloc[0]
            
            # The 10th trading day from t0
            if len(future_prices) > 10:
                price_t10 = future_prices.iloc[10]
                ret_10d = (price_t10 - price_t0) / price_t0
                direction = 1 if ret_10d > 0 else 0
                
                targets_10d.append(ret_10d)
                targets_direction.append(direction)
            else:
                targets_10d.append(np.nan)
                targets_direction.append(np.nan)
        except Exception as e:
            print(f"Error processing {ticker} at {t_date}: {e}")
            targets_10d.append(np.nan)
            targets_direction.append(np.nan)
            
    df['Target_10d_Return'] = targets_10d
    df['Target_10d_Direction'] = targets_direction
    
    # Drop rows where we couldn't fetch future data (e.g., date is too close to today)
    orig_len = len(df)
    df = df.dropna(subset=['Target_10d_Return'])
    print(f"Dropped {orig_len - len(df)} rows due to missing future price data.")
    
    df.to_csv("ml_dataset_final.csv", index=False)
    print(f"Saved ml_dataset_final.csv with shape {df.shape}.")

if __name__ == "__main__":
    fetch_and_merge()
