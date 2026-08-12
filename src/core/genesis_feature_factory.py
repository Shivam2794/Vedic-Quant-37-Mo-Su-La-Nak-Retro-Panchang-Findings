import pandas as pd
import numpy as np

print("Loading pristine continuous history matrix...")
df = pd.read_parquet('C:/Users/patel/Desktop/Python/Learn/full_history_astro_matrix.parquet')
df['Date'] = pd.to_datetime(df['Date'])
df.sort_values('Date', inplace=True)
df.reset_index(drop=True, inplace=True)

# Identify base numeric features to expand
exclude_cols = ['Date', 'Ticker', 'Year', 'Quarter']
numeric_cols = [c for c in df.columns if c not in exclude_cols and pd.api.types.is_numeric_dtype(df[c])]

df[numeric_cols] = df[numeric_cols].fillna(0)

print(f"Expanding {len(numeric_cols)} base features into lags and velocity combinations...")
lags = [1, 3, 5, 10, 20]
diffs = [3, 5]

new_features = {}

for c in numeric_cols:
    series = df[c]
    # Time-Lags (Phase & Momentum)
    for l in lags:
        new_features[f"{c}_lag{l}"] = series.shift(l).astype(np.float32)
    
    # Velocity Deltas (Rate of Change)
    for d in diffs:
        new_features[f"{c}_diff{d}"] = series.diff(d).astype(np.float32)

print("Concatenating 9000+ continuous features...")
df_expanded = pd.concat([df, pd.DataFrame(new_features)], axis=1)

print("Dropping first 20 rows created by lag20...")
df_expanded = df_expanded.iloc[20:].reset_index(drop=True)

print(f"Final Meticulous Shape: {df_expanded.shape}")
print("Saving to genesis_9000_continuous.parquet ...")
df_expanded.to_parquet('genesis_9000_continuous.parquet')
print("Done! The Continuous Engine is ready.")
