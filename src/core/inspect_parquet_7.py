import pandas as pd
import numpy as np
import json

def inspect_parquet():
    file_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet"
    try:
        df = pd.read_parquet(file_path)
        
        # Check for duplicates WITHIN the features array of each row
        def has_duplicates(feats):
            return len(feats) != len(set(feats))
            
        def get_duplicates(feats):
            seen = set()
            dups = set()
            for f in feats:
                if f in seen:
                    dups.add(f)
                seen.add(f)
            return list(dups)
            
        df['has_dup'] = df['features'].apply(has_duplicates)
        df_dups = df[df['has_dup']]
        
        sample_dups = []
        if len(df_dups) > 0:
            for idx, row in df_dups.head(10).iterrows():
                dups = get_duplicates(row['features'])
                sample_dups.append({
                    "row_index": idx,
                    "duplicate_features": dups,
                    "total_features": len(row['features']),
                    "unique_features": len(set(row['features']))
                })
                
        result = {
            "num_rows": len(df),
            "rows_with_internal_duplicates": len(df_dups),
            "samples": sample_dups
        }
        
        print(json.dumps(result, indent=2))
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_parquet()
