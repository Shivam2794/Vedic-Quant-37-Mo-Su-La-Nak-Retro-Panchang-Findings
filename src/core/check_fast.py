import pandas as pd
import json

try:
    df = pd.read_parquet(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet')
    
    unique_scores = df['score'].nunique()
    
    # anchors is a dictionary, we can convert it to string easily and check uniqueness
    df['anchor_str'] = df['anchors'].apply(str)
    unique_anchors = df['anchor_str'].nunique()
    
    # rank column
    unique_ranks = df['rank'].nunique()
    
    out = {
        "total_rows": len(df),
        "unique_scores": int(unique_scores),
        "unique_anchors": int(unique_anchors),
        "unique_ranks": int(unique_ranks)
    }
    
    with open('output_fast.json', 'w') as f:
        json.dump(out, f, indent=2)
except Exception as e:
    with open('output_fast.json', 'w') as f:
        json.dump({"error": str(e)}, f)
