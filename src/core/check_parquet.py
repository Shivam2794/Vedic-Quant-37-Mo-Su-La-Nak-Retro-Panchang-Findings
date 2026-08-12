import os
try:
    import pandas as pd
    df = pd.read_parquet(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet')
    print("Columns:", df.columns)
    print(df.head())
except Exception as e:
    print(f"Error: {e}")
