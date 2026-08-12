import pandas as pd
import sys

parquet_file = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\data_lake\orion_batch_SPY_TRADING_enriched\enriched_full.parquet"
try:
    df = pd.read_parquet(parquet_file)
    print(f"Shape: {df.shape}")
    print(f"Index: {df.index.name} or Columns: {list(df.columns)[:5]}")
    
    # Check prefixes
    prefixes = set([c.split('_')[0] for c in df.columns if '_' in c])
    print(f"Common column prefixes: {list(prefixes)[:10]}")
    
    # Null counts
    nulls = df.isnull().sum().sum()
    print(f"Total Nulls: {nulls}")
    
    # Number of features
    print(f"Total Columns: {len(df.columns)}")
    
    # Verify prefix for joining without duplicate columns
    # We should see something like 'SPY' or 'SPY_TRADE'
    
except Exception as e:
    print(f"Error: {e}")
