import pandas as pd
import numpy as np
import json

def inspect_parquet():
    file_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet"
    try:
        df = pd.read_parquet(file_path)
        
        # Sort features and join with comma
        def sort_features(feats):
            return ",".join(sorted(feats))
            
        df['sorted_features'] = df['features'].apply(sort_features)
        
        num_feature_duplicates = df['sorted_features'].duplicated().sum()
        dup_mask = df['sorted_features'].duplicated(keep=False)
        dup_rows = df[dup_mask]
        
        # Format the duplicate samples
        sample_dups = []
        if num_feature_duplicates > 0:
            # group by sorted_features to see the exact ones
            grouped = dup_rows.groupby('sorted_features')
            for name, group in list(grouped)[:5]:
                indices = group.index.tolist()
                sample_dups.append({
                    "sorted_features": name,
                    "indices": indices,
                    "count": len(indices)
                })
                
        result = {
            "num_rows": len(df),
            "num_feature_duplicates": int(num_feature_duplicates),
            "duplicate_groups": sample_dups
        }
        
        print(json.dumps(result, indent=2))
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_parquet()
