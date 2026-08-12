import pandas as pd
import numpy as np

df = pd.read_parquet(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet')

print(f"Total rows: {len(df)}")

def make_hashable(x):
    if isinstance(x, np.ndarray):
        return ",".join(map(str, x))
    return x

features_hashed = df['features'].apply(make_hashable)

dupes = features_hashed.duplicated()
num_dupes = dupes.sum()
print(f"Duplicates in features: {num_dupes}")

if num_dupes > 0:
    print("\nDuplicate blocks found!")
    # Get the value counts of the duplicated features
    val_counts = features_hashed.value_counts()
    duplicates_only = val_counts[val_counts > 1]
    print(f"Number of unique feature blocks that have duplicates: {len(duplicates_only)}")
    print(f"Total rows involved in duplicates: {duplicates_only.sum()}")
    print("\nSample of duplicate blocks and their frequencies:")
    print(duplicates_only.head(10))

    # check if 'score', 'confidence', etc. are also exactly the same for these duplicate blocks
    # which would indicate concurrent write collisions where the exact same data was written multiple times
    
    # Let's count how many exact rows there are if we hash features correctly
    df_hashable = df.copy()
    for col in df_hashable.columns:
        if col == 'features':
            df_hashable[col] = features_hashed
        elif isinstance(df_hashable[col].iloc[0], dict):
            import json
            df_hashable[col] = df_hashable[col].apply(lambda x: json.dumps(x, sort_keys=True))
            
    print(f"\nExact duplicate rows across ALL columns: {df_hashable.duplicated().sum()}")
