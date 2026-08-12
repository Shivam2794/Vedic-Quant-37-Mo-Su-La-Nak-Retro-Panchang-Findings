import os
import pandas as pd

def find_data():
    base_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith('.parquet') or f.endswith('.csv'):
                path = os.path.join(root, f)
                try:
                    if f.endswith('.parquet'):
                        df = pd.read_parquet(path)
                    else:
                        df = pd.read_csv(path, nrows=0)
                    
                    print(f"File: {f}, Path: {path}, Columns: {len(df.columns)}")
                    if 'orion' in f.lower() or len(df.columns) == 1013:
                        print(f"!!! MATCH !!! {f} has {len(df.columns)} columns")
                except Exception as e:
                    print(f"Error reading {f}: {e}")

if __name__ == "__main__":
    find_data()
