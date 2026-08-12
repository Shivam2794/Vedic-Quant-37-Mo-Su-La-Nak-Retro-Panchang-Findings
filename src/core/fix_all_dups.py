import pandas as pd
import glob

files = glob.glob(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\data_lake\**\enriched_full.parquet", recursive=True)

for f in files:
    try:
        df = pd.read_parquet(f)
        if 'timestamp' in df.columns:
            uniques = df['timestamp'].nunique()
            if uniques < len(df):
                print(f"Fixing {f}...")
                print(f"  Original shape: {df.shape}")
                df_dedup = df.drop_duplicates(subset=['timestamp'], keep='last')
                print(f"  Deduplicated shape: {df_dedup.shape}")
                df_dedup.to_parquet(f, engine='pyarrow', index=False)
                print(f"  Saved.")
    except Exception as e:
        print(f"Error processing {f}: {e}")
