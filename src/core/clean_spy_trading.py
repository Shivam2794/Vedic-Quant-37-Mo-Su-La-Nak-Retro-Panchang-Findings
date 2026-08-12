import pandas as pd
import sys
import os

parquet_file = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\data_lake\orion_batch_SPY_TRADING_enriched\enriched_full.parquet"
df = pd.read_parquet(parquet_file)

print(f"Original shape: {df.shape}")

# 1. Fill NaNs
if df['L8_Dasha_SAV_Resonance'].isnull().any():
    df['L8_Dasha_SAV_Resonance'] = df['L8_Dasha_SAV_Resonance'].fillna(0.0)
    print("Filled NaNs in L8_Dasha_SAV_Resonance with 0.0")

# 2. Add SPY_TRADE_ prefix to all columns except timestamp
new_cols = {}
for c in df.columns:
    if c != 'timestamp' and not c.startswith('SPY_TRADE_'):
        new_cols[c] = f"SPY_TRADE_{c}"

if new_cols:
    df = df.rename(columns=new_cols)
    print(f"Renamed {len(new_cols)} columns with 'SPY_TRADE_' prefix.")

# 3. Save back to parquet
df.to_parquet(parquet_file, index=False)
print("Saved cleaned and prefixed dataset back to parquet.")
