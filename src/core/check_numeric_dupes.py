import pandas as pd
import numpy as np

df = pd.read_parquet(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet')

# Let's check for rows that have the same score, confidence, and n_events
subset = ['score', 'confidence', 'n_events']
dupes = df.duplicated(subset=subset, keep=False)

print(f"Total rows: {len(df)}")
print(f"Rows with duplicated score, confidence, and n_events: {dupes.sum()}")

if dupes.sum() > 0:
    print(df[dupes].sort_values(by=['score']).head(20))
