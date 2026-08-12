import pandas as pd
import json

try:
    df = pd.read_parquet(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet')
    
    source_val = df['source'].iloc[0]
    out = {
        "columns": df.columns.tolist(),
        "total_rows": len(df),
        "source_type": str(type(source_val))
    }
    
    # Try to calculate unique values in the first column, which might be 'source'
    try:
        # If it's an array/list, we can stringify it to find uniques
        sources = df['source'].apply(str)
        out["unique_sources"] = int(sources.nunique())
        out["top_sources"] = sources.value_counts().head(25).to_dict()
    except Exception as e:
        out["error_unique"] = str(e)
        
    with open('output.json', 'w') as f:
        json.dump(out, f, indent=2)
except Exception as e:
    with open('output.json', 'w') as f:
        json.dump({"error": str(e)}, f)
