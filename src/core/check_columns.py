import pandas as pd

file_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\data_lake\orion_batch_DJIA_PUBLICATION_enriched\enriched_full.parquet"
df = pd.read_parquet(file_path)
print("Columns:", list(df.columns)[:20])
print(df.head())
