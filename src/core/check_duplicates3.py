import pandas as pd
import numpy as np

df = pd.read_parquet(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet')

print(f"Total rows: {len(df)}")

def make_hashable(x):
    if isinstance(x, np.ndarray):
        return x.tobytes()
    elif isinstance(x, list):
        return tuple(x)
    return x

df_hashable = df.copy()
for col in df_hashable.columns:
    df_hashable[col] = df_hashable[col].apply(make_hashable)

print(f"Total duplicates across all columns: {df_hashable.duplicated().sum()}")

for col in ['features', 'anchors']:
    if col in df_hashable.columns:
        dupes = df_hashable[col].duplicated().sum()
        print(f"Duplicates in {col}: {dupes}")

duplicates = df_hashable[df_hashable.duplicated(keep=False)]
if not duplicates.empty:
    print(f"\nTotal duplicate rows: {len(duplicates)}")
else:
    print("\nNo exact duplicate rows found.")
