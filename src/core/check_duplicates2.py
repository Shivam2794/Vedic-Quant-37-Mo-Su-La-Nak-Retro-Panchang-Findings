import pandas as pd
import numpy as np

df = pd.read_parquet(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet')

print(f"Total rows: {len(df)}")

# Convert unhashable types to string for duplication check
df_hashable = df.copy()
for col in df_hashable.columns:
    df_hashable[col] = df_hashable[col].apply(lambda x: str(x) if isinstance(x, (list, np.ndarray, dict)) else x)

print(f"Total duplicates across all columns: {df_hashable.duplicated().sum()}")

# Specifically check the tensor blocks if they exist. Maybe 'features' or 'anchors'?
for col in ['features', 'anchors']:
    if col in df_hashable.columns:
        dupes = df_hashable[col].duplicated().sum()
        print(f"Duplicates in {col}: {dupes}")

# Check for specific duplicate blocks across all columns
duplicates = df_hashable[df_hashable.duplicated(keep=False)]
if not duplicates.empty:
    print(f"\nTotal duplicate rows: {len(duplicates)}")
    print("Sample duplicate indices:")
    print(duplicates.index.tolist()[:20])
else:
    print("\nNo exact duplicate rows found.")
