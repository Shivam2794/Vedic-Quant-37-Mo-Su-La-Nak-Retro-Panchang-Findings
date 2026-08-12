import pandas as pd
import json

df = pd.read_parquet(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet')

print(f"Total rows: {len(df)}")
print(f"Total duplicates across all columns: {df.duplicated().sum()}")

# Check for duplicates on specific combinations if any
print("\nDuplicate counts by column:")
for col in df.columns:
    try:
        dupes = df[col].duplicated().sum()
        print(f"{col}: {dupes} duplicates")
    except Exception as e:
        print(f"Could not calculate duplicates for {col}: {e}")

# Check for blocks of duplicates
# A collision might mean multiple exact duplicate rows
duplicates = df[df.duplicated(keep=False)]
if not duplicates.empty:
    print("\nSome duplicate rows found:")
    print(duplicates.head(10))
    print(f"Total duplicate rows: {len(duplicates)}")
else:
    print("\nNo exact duplicate rows found.")

# Let's also check if 'features' or 'anchors' are byte arrays or something and have duplicates
