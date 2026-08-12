import os
import pandas as pd

search_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
target_keywords = ['orion', 'batch', 'djia', 'enriched', 'parquet']
found_path = None

for root, dirs, files in os.walk(search_dir):
    for f in files:
        f_lower = f.lower()
        if all(kw in f_lower for kw in target_keywords):
            found_path = os.path.join(root, f)
            break
    if found_path:
        break

if not found_path:
    print(f"File matching {target_keywords} not found in {search_dir}")
else:
    print(f"Found file at: {found_path}")
    try:
        df = pd.read_parquet(found_path)
        print(f"Dataset shape: {df.shape}")
        
        # Check for NaNs
        has_nans = df.isna().any().any()
        if has_nans:
            print("NaNs found in the feature columns.")
            nan_cols = df.columns[df.isna().any()].tolist()
            print(f"Columns with NaNs: {nan_cols[:10]}...") # print first 10
        else:
            print("No NaNs found in the dataset.")
            
    except Exception as e:
        print(f"Error reading parquet file: {e}")
