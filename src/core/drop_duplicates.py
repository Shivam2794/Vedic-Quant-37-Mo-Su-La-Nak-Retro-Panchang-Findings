import pandas as pd
import glob
import os

dir_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\data_lake\orion_batch_DJIA_PUBLICATION_enriched"
files = glob.glob(os.path.join(dir_path, "*.parquet"))

print(f"Loading parquet files: {files}")
df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
print(f"Original shape: {df.shape}")

df_dedup = df.drop_duplicates(subset=['timestamp'], keep='last')
print(f"Deduplicated shape: {df_dedup.shape}")

# Delete old files
for f in files:
    os.remove(f)

# Rewrite the parquet file as a single file
out_path = os.path.join(dir_path, "enriched_full.parquet")
df_dedup.to_parquet(out_path, engine='pyarrow', index=False)
print(f"Successfully written {out_path}.")
