import pandas as pd
import numpy as np
import json

def inspect_parquet():
    file_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet"
    try:
        df = pd.read_parquet(file_path)
        
        # Check any column for duplicates
        def to_serializable(val):
            if isinstance(val, np.ndarray):
                return val.tolist()
            if isinstance(val, dict):
                return str(val)
            return val
            
        result = {}
        for col in df.columns:
            if df[col].apply(lambda x: isinstance(x, (np.ndarray, list, dict))).any():
                df_col = df[col].apply(lambda x: str(x))
            else:
                df_col = df[col]
            
            num_dups = df_col.duplicated().sum()
            result[col] = int(num_dups)
            
        print(json.dumps(result, indent=2))
        
        print("Sample row:")
        row = df.iloc[0]
        print(json.dumps({k: to_serializable(v) for k, v in row.items()}, indent=2))

    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_parquet()
