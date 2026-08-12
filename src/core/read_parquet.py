import pyarrow.parquet as pq
import sys

try:
    path = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet'
    table = pq.read_table(path)
    df = table.to_pandas()
    print("Columns:", df.columns.tolist())
    print("\nDescribe:")
    print(df.describe())
    print("\nHead:")
    print(df.head())
except Exception as e:
    print(f"Error: {e}")
