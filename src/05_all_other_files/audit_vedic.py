import pandas as pd
import sys

def main():
    try:
        path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet"
        df = pd.read_parquet(path)
        print("Columns:", df.columns.tolist())
        print("Number of records:", len(df))
        print("Sample data:")
        print(df.head(3))
        
        if 'datetime' in df.columns:
            print("Unique datetimes:", df['datetime'].unique())
            
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
