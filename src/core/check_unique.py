import pandas as pd
import json

try:
    df = pd.read_parquet(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet')
    
    # Try to calculate unique values in features
    # features might be an array of strings
    try:
        features_tuples = df['features'].apply(lambda x: tuple(x) if isinstance(x, (list, tuple)) else tuple(x.tolist()) if hasattr(x, 'tolist') else str(x))
        unique_features = len(set(features_tuples))
        
        # also calculate unique values of entire rows
        # dropping the 'rank' or whatever is just an index
        df_hashable = df.copy()
        for col in df_hashable.columns:
            df_hashable[col] = df_hashable[col].apply(lambda x: tuple(x) if isinstance(x, (list, tuple)) else tuple(x.tolist()) if hasattr(x, 'tolist') else str(x))
            
        unique_rows = len(df_hashable.drop_duplicates())
        
        # let's count value_counts of features
        feature_counts = features_tuples.value_counts()
        
        out = {
            "unique_features": unique_features,
            "unique_rows": unique_rows,
            "top_10_feature_combinations": {str(k): int(v) for k, v in feature_counts.head(10).items()}
        }
    except Exception as e:
        out = {"error_unique": str(e)}
        
    with open('output_unique.json', 'w') as f:
        json.dump(out, f, indent=2)
except Exception as e:
    with open('output_unique.json', 'w') as f:
        json.dump({"error": str(e)}, f)
