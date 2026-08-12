import pandas as pd

parquet_file = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\data_lake\orion_batch_SPY_TRADING_enriched\enriched_full.parquet"
df = pd.read_parquet(parquet_file)

null_cols = df.isnull().sum()
null_cols = null_cols[null_cols > 0]
print("Columns with Nulls:")
print(null_cols)
