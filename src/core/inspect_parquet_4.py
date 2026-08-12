import pandas as pd
import numpy as np
import json

def inspect_parquet():
    file_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet"
    try:
        df = pd.read_parquet(file_path)
        
        # Check for exact feature duplicates in the 'features' column
        df_features = df['features'].astype(str)
        num_feature_duplicates = df_features.duplicated().sum()
        dup_mask = df_features.duplicated(keep=False)
        dup_rows = df[dup_mask]
        
        # Format the duplicate samples to be JSON serializable
        def to_serializable(val):
            if isinstance(val, np.ndarray):
                return val.tolist()
            if isinstance(val, dict):
                return str(val)
            return val
            
        sample_dups = []
        if num_feature_duplicates > 0:
            for _, row in dup_rows.head(10).iterrows():
                sample_dups.append({k: to_serializable(v) for k, v in row.items()})
                
        result = {
            "num_rows": len(df),
            "num_feature_duplicates": int(num_feature_duplicates),
            "duplicate_feature_samples": sample_dups
        }
        
        print(json.dumps(result, indent=2))
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_parquet()
