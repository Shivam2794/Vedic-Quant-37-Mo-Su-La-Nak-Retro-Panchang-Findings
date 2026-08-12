import pandas as pd
import numpy as np

df = pd.read_parquet(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet')

for col in df.columns:
    val = df[col].iloc[0]
    print(f"Column: {col}, Type: {type(val)}")
    if isinstance(val, np.ndarray):
        print(f"  Shape: {val.shape}")
    print(f"  Sample: {val}")
