import pandas as pd
import numpy as np
from collections import Counter
import json

def inspect_parquet():
    file_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet"
    try:
        df = pd.read_parquet(file_path)
        
        all_features = []
        for feats in df['features']:
            all_features.extend(feats)
            
        counts = Counter(all_features)
        most_common = counts.most_common(20)
        
        print("Total features instances:", len(all_features))
        print("Unique features:", len(counts))
        print("Most common features:")
        for feat, count in most_common:
            print(f"{feat}: {count}")

        # Let's check for features that appear exactly the same number of times as the number of rows?
        print("Number of rows:", len(df))

    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_parquet()
