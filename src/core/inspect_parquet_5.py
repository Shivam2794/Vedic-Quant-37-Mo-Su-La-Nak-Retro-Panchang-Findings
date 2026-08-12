import pandas as pd
import json

def inspect_parquet():
    file_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet"
    try:
        df = pd.read_parquet(file_path)
        print("Feature column type:", type(df['features'].iloc[0]))
        print("Sample 1:", df['features'].iloc[0])
        print("Sample 2:", df['features'].iloc[1])
        print("Sample 3:", df['features'].iloc[2])
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_parquet()
