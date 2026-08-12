import pyarrow.parquet as pq
import sys

file_path = "C:\\Users\\Shivam Patel\\.gemini\\antigravity\\scratch\\orion_pipeline\\smart_ml\\output\\orion_alpha_registry.parquet"

try:
    parquet_file = pq.ParquetFile(file_path)
    schema = parquet_file.schema
    print("Schema details:")
    print(schema)
    
    # Let's also check a few rows to see what it contains
    table = parquet_file.read()
    print("\nSample Data (first 3 rows):")
    print(table.slice(0, 3).to_pandas())
except Exception as e:
    print(f"Error reading Parquet file: {e}")
