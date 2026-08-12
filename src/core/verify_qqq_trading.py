import pandas as pd
import sys
import os

def verify_dataset():
    path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\data_lake\orion_batch_QQQ_TRADING_enriched"
    try:
        df = pd.read_parquet(path, engine='pyarrow')
    except Exception as e:
        print(f"Error loading dataset: {e}")
        sys.exit(1)

    print(f"--- QQQ_TRADING_enriched Dataset Verification ---")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"Duplicates: {df.duplicated().sum()}")
    
    if 'timestamp' in df.columns:
        print(f"Min Timestamp: {df['timestamp'].min()}")
        print(f"Max Timestamp: {df['timestamp'].max()}")
        
        # Check duplicate timestamps
        dupe_timestamps = df['timestamp'].duplicated().sum()
        print(f"Duplicate Timestamps: {dupe_timestamps}")
        
    else:
        print("WARNING: No 'timestamp' column found!")

    null_counts = df.isnull().sum()
    cols_with_nulls = null_counts[null_counts > 0]
    
    if len(cols_with_nulls) > 0:
        print("\nColumns with NaNs:")
        print(cols_with_nulls)
    else:
        print("\nNo NaNs found in any columns. Data is clean.")

if __name__ == "__main__":
    verify_dataset()
