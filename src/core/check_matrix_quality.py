import pyarrow.parquet as pq
import glob
import pandas as pd
import numpy as np

files = glob.glob(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\features_partitioned\**\*.parquet", recursive=True)
print(f"Total partitions generated: {len(files)}")

if not files:
    print("No files found!")
    exit()

# Sample a few files
sample_files = files[:3]
total_rows = 0

for f in sample_files:
    df = pd.read_parquet(f)
    print(f"\nChecking: {f}")
    print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
    total_rows += len(df)
    
    # Check for NaNs in target columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    nans = df[numeric_cols].isna().sum()
    print(f"Columns with NaNs: {len(nans[nans > 0])}")
    
    # Check if our new 740+ rules are there
    rule_cols = [c for c in df.columns if c.startswith('rule_')]
    ton_cols = [c for c in df.columns if c.startswith('ton_')]
    dasha_cols = [c for c in df.columns if c.startswith('dasha_')]
    
    print(f"PDF Rules count: {len(rule_cols)}")
    print(f"ML Transit-Over-Natal count: {len(ton_cols)}")
    print(f"ML Dasha count: {len(dasha_cols)}")
