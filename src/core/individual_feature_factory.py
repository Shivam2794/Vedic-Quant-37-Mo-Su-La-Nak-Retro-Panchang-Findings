import os
import sys
import pandas as pd
import numpy as np
import json
import time

sys.path.append(r"C:\Users\patel\Desktop\Python\Learn")
from build_stock_matrix import build_stock_features

print("="*70)
print(" GENESIS PHASE 8: INDIVIDUALIZED NATAL FEATURE FACTORY")
print("="*70)

# Paths
BASE_DIR = r"C:\Users\patel\Desktop\Python\Learn"
NATAL_MEMORY = os.path.join(BASE_DIR, "etf_natal_memory.json")
ASTRO_PATH = os.path.join(BASE_DIR, "AstroData_2004_2027.csv")
OUTPUT_DIR = r"C:\Users\patel\Desktop\Python\Learn"

# 1. Load Data
print("\n[1/3] Loading Master Ephemeris and Natal Memory...")
with open(NATAL_MEMORY, "r") as f:
    natal_memory = json.load(f)

astro = pd.read_csv(ASTRO_PATH)
astro["Date"] = pd.to_datetime(astro["Time"].astype(str), format="%Y%m%d")
astro = astro.set_index("Date").sort_index()
astro = astro[astro.index.dayofweek < 5] # Weekdays only
dates = astro.index.tolist()
print(f" Loaded {len(dates)} continuous trading days.")

# 2. Lag and Velocity Expansion Logic
def expand_features(df):
    new_features = {}
    base_cols = [c for c in df.columns if c not in ['Date', 'Ticker']]
    
    df.sort_values('Date', inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    # Pre-allocate for performance
    for c in base_cols:
        series = df[c]
        new_features[f"{c}_lag1"] = series.shift(1)
        new_features[f"{c}_lag3"] = series.shift(3)
        new_features[f"{c}_lag5"] = series.shift(5)
        new_features[f"{c}_lag10"] = series.shift(10)
        new_features[f"{c}_lag20"] = series.shift(20)
        
        # Velocity
        new_features[f"{c}_diff3"] = series.diff(3)
        new_features[f"{c}_diff10"] = series.diff(10)
        
    expanded_df = pd.DataFrame(new_features, index=df.index)
    df = pd.concat([df, expanded_df], axis=1)
    df.fillna(0, inplace=True)
    
    # Filter out 2004 since it has NaN lags
    df = df[df['Date'] >= pd.to_datetime('2005-01-01')]
    return df

# 3. Process Each Ticker
tickers = list(natal_memory.keys())
print(f"\n[2/3] Processing {len(tickers)} Assets Individually...")

for idx, ticker in enumerate(tickers):
    t0 = time.time()
    out_file = os.path.join(OUTPUT_DIR, f"genesis_9000_{ticker}.parquet")
    
    if os.path.exists(out_file):
        print(f" [{idx+1}/{len(tickers)}] {ticker} already processed. Skipping.")
        continue
        
    print(f" [{idx+1}/{len(tickers)}] Calculating Natal Transits for {ticker}...")
    
    try:
        natal = natal_memory[ticker]
        # Generate base 1240 features (Natal Transits)
        base_df = build_stock_features(ticker, natal, astro, dates)
        
        if base_df.empty:
            print(f"   ERROR: Empty base matrix for {ticker}")
            continue
            
        # Expand to 9000 features
        final_df = expand_features(base_df)
        
        # Convert types to save space
        float_cols = final_df.select_dtypes(include=['float64']).columns
        final_df[float_cols] = final_df[float_cols].astype('float32')
        
        # Save
        final_df.to_parquet(out_file)
        print(f"   SUCCESS! Saved {len(final_df.columns)} features. Time: {time.time()-t0:.1f}s")
        
    except Exception as e:
        print(f"   ERROR processing {ticker}: {e}")

print("\n[3/3] Done. All assets have unique continuous matrices.")
