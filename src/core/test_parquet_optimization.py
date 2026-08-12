import os
import json
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Paths
original_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet"
optimized_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry_optimized.parquet"

# Load original
df = pd.read_parquet(original_path)

# 1. Extract anchors and drop column
anchors_dict = df["anchors"].iloc[0] if "anchors" in df.columns and not df.empty else {}
if "anchors" in df.columns:
    df = df.drop(columns=["anchors"])

# 2. Categorical encoding
if "source" in df.columns:
    df["source"] = df["source"].astype("category")

# 3. Downcasting
float_cols = ["confidence", "lift", "score", "score_norm"]
int_cols = ["n_events", "rank"]

for col in float_cols:
    if col in df.columns:
        df[col] = df[col].astype("float32")
        
for col in int_cols:
    if col in df.columns:
        df[col] = df[col].astype("int32")

# Write optimized with custom metadata
table = pa.Table.from_pandas(df)
custom_metadata = table.schema.metadata
if custom_metadata is None:
    custom_metadata = {}
    
# Store anchors in metadata
custom_metadata[b"anchors"] = json.dumps(anchors_dict).encode("utf-8")
table = table.replace_schema_metadata(custom_metadata)

pq.write_table(table, optimized_path)

# Compare
orig_size = os.path.getsize(original_path)
opt_size = os.path.getsize(optimized_path)
reduction = (orig_size - opt_size) / orig_size * 100

print(f"Original size: {orig_size} bytes")
print(f"Optimized size: {opt_size} bytes")
print(f"Reduction: {reduction:.2f}%")

print("\n--- Optimized Schema ---")
print(table.schema)
