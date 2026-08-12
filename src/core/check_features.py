import pandas as pd
import numpy as np

df = pd.read_parquet(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet')

print("Type of features:", type(df['features'].iloc[0]))
if isinstance(df['features'].iloc[0], np.ndarray):
    print("Shape of features[0]:", df['features'].iloc[0].shape)
    
print("First few features:")
print(df['features'].head())
