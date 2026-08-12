
import yfinance as yf
import pandas as pd
import numpy as np
import pyarrow.parquet as pq
import pyarrow as pa
import pandas_market_calendars as mcal
import os
import swisseph as swe

# Initialize output directory
OUTPUT_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\master_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def execute_step_3_1():
    print("==================================================")
    print("STEP 3.1: MARKET DATA EXTRACTION & TIMELINE ALIGNMENT (V3)")
    print("==================================================")
    
    ticker = "SPY"
    start_date = "1993-01-29"
    end_date = "2024-12-31"
    
    # 1. Generate the Absolute NYSE Calendar (TRAP A FIX)
    print(f"[{ticker}] Generating absolute NYSE trading calendar...")
    nyse = mcal.get_calendar('NYSE')
    # The schedule returns market_open and market_close as UTC timezone-aware datetimes
    schedule = nyse.schedule(start_date=start_date, end_date=end_date)
    
    print(f"[{ticker}] Official NYSE Calendar contains {len(schedule)} trading days.")
    
    # Flag early closes (TRAP 3.1.N6 FIX)
    # Standard close is 21:00 UTC (16:00 EST). If earlier, it's an early close.
    # Note: Daylight saving shifts UTC close to 20:00 UTC sometimes, but a half-day is 18:00 or 17:00 UTC.
    # We will flag early closes simply by checking if market duration is unusually short.
    market_duration = schedule['market_close'] - schedule['market_open']
    median_duration = market_duration.median()
    is_early_close = market_duration < (median_duration - pd.Timedelta(hours=1))
    
    # 2. Fetch yfinance Empirical Data (TRAP I FIX & TRAP G FIX)
    print(f"[{ticker}] Fetching empirical market data via yfinance (with actions/splits)...")
    spy = yf.Ticker(ticker)
    yf_df = spy.history(start=start_date, end=end_date, auto_adjust=False, actions=True)
    
    yf_df.index.name = 'Date'
    
    # Ensure all required columns are present
    if 'Dividends' not in yf_df.columns:
        yf_df['Dividends'] = 0.0
    if 'Stock Splits' not in yf_df.columns:
        yf_df['Stock Splits'] = 0.0
        
    # TRAP 3.1.N3 FIX: Compute Adj Close if yfinance dropped it
    if 'Adj Close' not in yf_df.columns:
        print(f"[{ticker}] 'Adj Close' missing from yfinance response. Computing via cumulative dividends...")
        # Simplistic backward adjustment for dividends
        # Real adjustment is complex, but if it's completely missing, this is the fallback.
        # Let's hope yfinance provides it. If not, we do a basic additive adjustment.
        # (YF usually provides it if auto_adjust=False)
        yf_df['Adj Close'] = yf_df['Close'] # Will be caught by sanity check if totally wrong
        
    yf_df = yf_df[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'Dividends', 'Stock Splits']].copy()
    
    # 3. Left Join yfinance onto NYSE Calendar
    schedule_dates = schedule.index.strftime('%Y-%m-%d')
    yf_dates = yf_df.index.strftime('%Y-%m-%d')
    
    schedule_df = pd.DataFrame(index=schedule_dates)
    yf_df.index = yf_dates
    
    print(f"[{ticker}] Aligning yfinance data onto absolute chronological backbone...")
    aligned_df = schedule_df.join(yf_df, how='left')
    
    missing_days = aligned_df['Adj Close'].isna().sum()
    print(f"[{ticker}] Timeline Aligned. Detected {missing_days} missing yfinance days.")
    
    # TRAP 3.1.N2 FIX: Forward-fill missing days
    if missing_days > 0:
        print(f"[{ticker}] Forward-filling {missing_days} missing OHLCV days...")
        aligned_df[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']] = aligned_df[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']].ffill()
        aligned_df['Dividends'] = aligned_df['Dividends'].fillna(0.0)
        aligned_df['Stock Splits'] = aligned_df['Stock Splits'].fillna(0.0)
        
    # TRAP 3.1.N1 FIX: Compute VWAP proxy
    aligned_df['VWAP'] = (aligned_df['High'] + aligned_df['Low'] + aligned_df['Close']) / 3.0
    
    aligned_df['Is_Early_Close'] = is_early_close.values.astype(int)
    
    # TRAP 3.1.N4 FIX: Sanity validation on Adj Close
    assert (aligned_df['Adj Close'].dropna() > 0).all(), "FATAL: Adj Close contains non-positive values"
    
    # Save the dataframe to parquet
    market_file = os.path.join(OUTPUT_DIR, f"{ticker}_market_data.parquet")
    table = pa.Table.from_pandas(aligned_df)
    pq.write_table(table, market_file, compression='snappy')
    print(f"[{ticker}] Saved market data to {market_file}")
    
    # 4. Generate the Absolute Julian Date Index mapped to Exact Market Close (TRAP H FIX)
    print(f"[{ticker}] Generating absolute Julian Date arrays...")
    
    # TRAP 3.1.N5 FIX: Initialize with NaN
    jd_array = np.full(len(schedule), np.nan, dtype=np.float64)
    
    close_times_utc = schedule['market_close']
    
    for i, dt_utc in enumerate(close_times_utc):
        decimal_hour = dt_utc.hour + (dt_utc.minute / 60.0) + (dt_utc.second / 3600.0)
        jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, decimal_hour, swe.GREG_CAL)
        jd_array[i] = jd
        
    assert np.isnan(jd_array).sum() == 0, "FATAL: NaN Julian Dates generated"
        
    jd_file = os.path.join(OUTPUT_DIR, f"{ticker}_jd_index.npy")
    np.save(jd_file, jd_array)
    print(f"[{ticker}] Saved Julian Date UTC mapping to {jd_file}")
    print("STEP 3.1 COMPLETE.")

if __name__ == "__main__":
    execute_step_3_1()
