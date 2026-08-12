import pandas as pd

file_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\data_lake\orion_batch_DJIA_PUBLICATION_enriched\enriched_full.parquet"
df = pd.read_parquet(file_path)
print("Original shape:", df.shape)
print("Unique timestamps:", df['timestamp'].nunique())
df_dedup = df.drop_duplicates(subset=['timestamp'], keep='last')
print("Deduplicated shape:", df_dedup.shape)
