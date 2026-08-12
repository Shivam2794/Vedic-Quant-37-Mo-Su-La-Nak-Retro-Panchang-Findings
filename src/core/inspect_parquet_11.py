import pandas as pd
from collections import defaultdict
import json

def inspect_parquet():
    file_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet"
    try:
        df = pd.read_parquet(file_path)
        
        feature_to_rows = defaultdict(set)
        for idx, feats in enumerate(df['features']):
            for f in feats:
                feature_to_rows[f].add(idx)
                
        rowset_to_features = defaultdict(list)
        for f, rows in feature_to_rows.items():
            row_tuple = tuple(sorted(list(rows)))
            rowset_to_features[row_tuple].append(f)
            
        duplicate_groups = []
        for row_tuple, feats in rowset_to_features.items():
            if len(feats) > 1:
                # To distinguish between "accidentally co-occurring once" and "systematic loop",
                # check if they occur in a significant number of rows together, or just more than 1
                if len(row_tuple) > 10:
                    duplicate_groups.append({
                        "features": sorted(feats),
                        "row_count": len(row_tuple)
                    })
                
        print(f"Found {len(duplicate_groups)} groups of exact duplicate features (co-occurring > 10 rows).")
        for g in duplicate_groups:
            print(f"Features: {g['features']} | Rows: {g['row_count']}")

    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_parquet()
