import pandas as pd
from collections import defaultdict
import json

def inspect_parquet():
    file_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet"
    try:
        df = pd.read_parquet(file_path)
        
        # Track which rows each feature appears in
        feature_to_rows = defaultdict(set)
        for idx, feats in enumerate(df['features']):
            for f in feats:
                feature_to_rows[f].add(idx)
                
        # Group features by their exact row sets
        rowset_to_features = defaultdict(list)
        for f, rows in feature_to_rows.items():
            # Create a sorted tuple of row indices to use as a dictionary key
            row_tuple = tuple(sorted(list(rows)))
            rowset_to_features[row_tuple].append(f)
            
        duplicates = {}
        for row_tuple, feats in rowset_to_features.items():
            if len(feats) > 1:
                # We found multiple features that appear in the exact same set of rows!
                duplicates[str(feats)] = len(row_tuple)
                
        print(f"Found {len(duplicates)} groups of exact duplicate features.")
        if duplicates:
            print("Duplicate feature groups and their occurrence count:")
            for feats, count in duplicates.items():
                print(f"{feats} appears in exactly {count} rows together")

    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_parquet()
