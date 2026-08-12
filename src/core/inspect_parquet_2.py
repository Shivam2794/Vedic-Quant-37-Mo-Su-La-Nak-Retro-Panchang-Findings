import pandas as pd
import numpy as np
import json

def inspect_parquet():
    file_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet"
    try:
        df = pd.read_parquet(file_path)
        
        # Convert arrays to tuples so they can be hashed
        df_hashable = pd.DataFrame()
        for col in df.columns:
            if df[col].apply(lambda x: isinstance(x, np.ndarray) or isinstance(x, list)).any():
                df_hashable[col] = df[col].apply(lambda x: tuple(x) if isinstance(x, (np.ndarray, list)) else x)
            else:
                df_hashable[col] = df[col]
                
        num_duplicates = df_hashable.duplicated().sum()
        dup_mask = df_hashable.duplicated(keep=False)
        dup_rows = df[dup_mask]
        
        # Format the duplicate samples to be JSON serializable
        def to_serializable(val):
            if isinstance(val, np.ndarray):
                return val.tolist()
            return val
            
        sample_dups = []
        if num_duplicates > 0:
            for _, row in dup_rows.head(10).iterrows():
                sample_dups.append({k: to_serializable(v) for k, v in row.items()})
                
        result = {
            "num_rows": len(df),
            "num_columns": len(df.columns),
            "columns": list(df.columns),
            "num_duplicates": int(num_duplicates),
            "duplicate_samples": sample_dups
        }
        
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_parquet()
