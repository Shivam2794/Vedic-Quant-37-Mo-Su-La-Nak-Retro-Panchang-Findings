import pandas as pd
import numpy as np

df = pd.read_parquet(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet')

def make_set_hashable(x):
    if isinstance(x, np.ndarray):
        return ",".join(sorted(map(str, x)))
    return x

features_hashed = df['features'].apply(make_set_hashable)

dupes = features_hashed.duplicated()
num_dupes = dupes.sum()
print(f"Duplicates in feature sets (ignoring order): {num_dupes}")

if num_dupes > 0:
    print(f"\nDuplicate sets found: {num_dupes}")
    val_counts = features_hashed.value_counts()
    duplicates_only = val_counts[val_counts > 1]
    print(duplicates_only.head())
