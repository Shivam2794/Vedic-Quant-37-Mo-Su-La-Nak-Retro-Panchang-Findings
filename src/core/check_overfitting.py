import pandas as pd

try:
    df = pd.read_parquet(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet')
    print("First 5 rows of source:")
    print(df['source'].head())
    print("\nNumber of unique source values:")
    print(df['source'].nunique())
    
    print("\nValue counts for source (top 10):")
    print(df['source'].value_counts().head(10))
    
    print("\nFirst 5 rows of features:")
    print(df['features'].head())
    
    print("\nFirst 5 rows of anchors:")
    print(df['anchors'].head())
except Exception as e:
    print(f"Error: {e}")
