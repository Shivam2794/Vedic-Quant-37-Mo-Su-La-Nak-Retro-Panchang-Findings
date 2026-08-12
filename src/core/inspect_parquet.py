import pandas as pd
import json

def inspect_parquet():
    file_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet"
    try:
        df = pd.read_parquet(file_path)
        # Check for exact feature duplicates (rows that are exactly the same)
        num_duplicates = df.duplicated().sum()
        dup_rows = df[df.duplicated(keep=False)]
        
        result = {
            "num_rows": len(df),
            "num_columns": len(df.columns),
            "columns": list(df.columns),
            "num_duplicates": int(num_duplicates),
            "duplicate_samples": dup_rows.head(10).to_dict(orient="records") if num_duplicates > 0 else []
        }
        
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_parquet()
