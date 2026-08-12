import pandas as pd
import glob

files = glob.glob(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\data_lake\**\enriched_full.parquet", recursive=True)

for f in files:
    try:
        df = pd.read_parquet(f)
        print(f"\nFile: {f}")
        print(f"Original shape: {df.shape}")
        if 'timestamp' in df.columns:
            uniques = df['timestamp'].nunique()
            print(f"Unique timestamps: {uniques}")
            if uniques < len(df):
                print(f"DUPLICATES DETECTED: {len(df) - uniques}")
    except Exception as e:
        print(f"Error reading {f}: {e}")
