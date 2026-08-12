import pyarrow.parquet as pq

file_path = "C:\\Users\\Shivam Patel\\.gemini\\antigravity\\scratch\\orion_pipeline\\smart_ml\\output\\orion_alpha_registry.parquet"
parquet_file = pq.ParquetFile(file_path)

meta = parquet_file.metadata
print(f"Number of row groups: {meta.num_row_groups}")
for i in range(meta.num_row_groups):
    rg = meta.row_group(i)
    for j in range(rg.num_columns):
        col = rg.column(j)
        print(f"Column {j} ({col.path_in_schema}): Compression = {col.compression}")
