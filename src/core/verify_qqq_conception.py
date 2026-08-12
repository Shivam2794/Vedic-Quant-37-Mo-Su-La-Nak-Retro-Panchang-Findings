import pandas as pd
import numpy as np

file_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\data_lake\orion_batch_QQQ_CONCEPTION_enriched\enriched_full.parquet"

try:
    df = pd.read_parquet(file_path)
    print("=== Verification of orion_batch_QQQ_CONCEPTION_enriched ===")
    print(f"Shape: {df.shape}")
    print("\nColumns:")
    print(df.columns.tolist())
    
    print("\nMissing values per column:")
    missing = df.isnull().sum()
    print(missing[missing > 0])
    
    print("\nData Types:")
    print(df.dtypes.value_counts())
    
    print("\nSample Data:")
    print(df.head(3))
    
    # Specific stats on any key columns if present, such as date ranges
    datetime_cols = df.select_dtypes(include=['datetime64', 'object']).columns
    if 'date' in df.columns or 'timestamp' in df.columns or 'time' in df.columns:
        date_col = 'date' if 'date' in df.columns else ('timestamp' if 'timestamp' in df.columns else 'time')
        print(f"\nDate range in {date_col}:")
        print(f"Min: {df[date_col].min()}, Max: {df[date_col].max()}")
        
except Exception as e:
    print(f"Error reading parquet file: {e}")
