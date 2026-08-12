import pandas as pd
import os
import re

def verify():
    output_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output"
    boolean_file = os.path.join(output_dir, "boolean_itemsets.parquet")
    registry_file = os.path.join(output_dir, "orion_alpha_registry.parquet")
    tensor_file = os.path.join(output_dir, "feature_tensor.parquet")

    results = []

    # 1. Check if feature_tensor.parquet is missing
    missing_tensor = not os.path.exists(tensor_file)
    results.append(f"1. Missing feature_tensor.parquet: {missing_tensor}")

    # 2. Check boolean_itemsets.parquet columns
    if os.path.exists(boolean_file):
        df_bool = pd.read_parquet(boolean_file)
        cols = list(df_bool.columns)
        all_feat_x = all(re.match(r"^feat_\d+$", c) for c in cols)
        results.append(f"2. boolean_itemsets.parquet has {len(cols)} columns, all matching 'feat_X': {all_feat_x}")
    else:
        results.append("2. boolean_itemsets.parquet not found.")

    # 3. Check orion_alpha_registry.parquet features
    if os.path.exists(registry_file):
        df_reg = pd.read_parquet(registry_file)
        # Extract all unique features across all rows
        all_features = set()
        for feats in df_reg['features']:
            all_features.update(feats)
        all_feat_x_reg = all(re.match(r"^feat_\d+$", f) for f in all_features)
        results.append(f"3. orion_alpha_registry.parquet uses only 'feat_X' labels: {all_feat_x_reg}")
        
    print("\n".join(results))

if __name__ == "__main__":
    verify()
