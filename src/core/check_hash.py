import pandas as pd
import json
import hashlib

try:
    df = pd.read_parquet(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet')
    
    def hash_row(row):
        # Create a string representation of the row to hash
        row_str = str(row['source']) + str(row['features']) + str(row['anchors']) + str(row['score'])
        return hashlib.md5(row_str.encode('utf-8')).hexdigest()
        
    df['row_hash'] = df.apply(hash_row, axis=1)
    
    unique_hashes = df['row_hash'].nunique()
    
    # Also let's check unique anchors
    df['anchor_str'] = df['anchors'].apply(str)
    unique_anchors = df['anchor_str'].nunique()
    
    # Check unique scores
    unique_scores = df['score'].nunique()
    
    out = {
        "total_rows": len(df),
        "unique_exact_rows_by_hash": int(unique_hashes),
        "unique_anchors": int(unique_anchors),
        "unique_scores": int(unique_scores)
    }
    
    with open('output_hash.json', 'w') as f:
        json.dump(out, f, indent=2)
except Exception as e:
    with open('output_hash.json', 'w') as f:
        json.dump({"error": str(e)}, f)
