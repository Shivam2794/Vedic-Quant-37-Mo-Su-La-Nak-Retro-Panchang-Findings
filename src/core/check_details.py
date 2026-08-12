import pandas as pd
import json

try:
    df = pd.read_parquet(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet')
    
    out = {
        "features_head": [str(x) for x in df['features'].head(3).tolist()],
        "anchors_head": [str(x) for x in df['anchors'].head(3).tolist()]
    }
    
    with open('output_details.json', 'w') as f:
        json.dump(out, f, indent=2)
except Exception as e:
    with open('output_details.json', 'w') as f:
        json.dump({"error": str(e)}, f)
