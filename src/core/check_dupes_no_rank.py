import pandas as pd
import numpy as np

df = pd.read_parquet(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet')

def make_hashable(x):
    if isinstance(x, np.ndarray):
        return ",".join(map(str, x))
    elif isinstance(x, dict):
        import json
        return json.dumps(x, sort_keys=True)
    return x

df_hashable = df.copy()
for col in df_hashable.columns:
    df_hashable[col] = df_hashable[col].apply(make_hashable)

# Drop rank column
df_no_rank = df_hashable.drop(columns=['rank'])

print(f"Total rows: {len(df)}")
dupes = df_no_rank.duplicated(keep=False)
num_dupes = dupes.sum()
print(f"Exact duplicate rows ignoring 'rank': {num_dupes}")

if num_dupes > 0:
    print(df_no_rank[dupes].head(20))
