import pandas as pd
file_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\data_lake\orion_batch_SPY_CONCEPTION_enriched\enriched_full.parquet"
try:
    df = pd.read_parquet(file_path)
    print("=== Dataset Shape ===")
    print(df.shape)
    print("\n=== Dataset Info ===")
    df.info(verbose=True, show_counts=True)
    print("\n=== Sample Data ===")
    print(df.head())
except Exception as e:
    print(f"Error reading parquet file: {e}")
