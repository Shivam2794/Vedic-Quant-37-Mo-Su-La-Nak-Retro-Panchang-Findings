import pandas as pd

try:
    df = pd.read_parquet(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet')
    print("DataFrame shape:", df.shape)
    
    print("\nSource column type:", type(df['source'].iloc[0]))
    print("Source head:", df['source'].head(5).tolist())
    
    # Try to make a set out of the source column if it's strings/ints
    try:
        if isinstance(df['source'].iloc[0], (str, int, float, bool)):
            unique_sources = df['source'].nunique()
            print("Unique source values:", unique_sources)
        elif isinstance(df['source'].iloc[0], (list, tuple)):
            # convert lists to tuples
            sources = df['source'].apply(tuple)
            unique_sources = sources.nunique()
            print("Unique source tuples:", unique_sources)
        else:
            print("Source is some other type:", type(df['source'].iloc[0]))
    except Exception as e:
        print("Error checking unique sources:", e)
        
    print("\nAnchors column type:", type(df['anchors'].iloc[0]))
    print("Anchors head:", df['anchors'].head(5).tolist())
except Exception as e:
    print(f"Error: {e}")
