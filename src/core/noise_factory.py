import os
import sys
import pandas as pd
import numpy as np
import time

print("="*70)
print(" GENESIS PHASE 11: THE NULL HYPOTHESIS NOISE FACTORY")
print("="*70)

BASE_DIR = r"C:\Users\patel\Desktop\Python\Learn"
SOURCE_FILE = os.path.join(BASE_DIR, "genesis_9000_MUNDANE.parquet")
OUTPUT_FILE = os.path.join(BASE_DIR, "genesis_9000_NOISE.parquet")

print("\n[1/2] Loading template architecture...")
t0 = time.time()
df = pd.read_parquet(SOURCE_FILE)
cols = [c for c in df.columns if c not in ['Date', 'Ticker']]

print(f"  Template loaded. {len(cols)} numerical features, {len(df)} days.")

print("\n[2/2] Overwriting universe with Pure Gaussian Noise...")
# Generate identical shaped random noise
noise_data = np.random.randn(len(df), len(cols)).astype(np.float32)

# Replace all values
df[cols] = noise_data

df.to_parquet(OUTPUT_FILE)
print(f"  SUCCESS! Saved pure noise matrix to genesis_9000_NOISE.parquet in {time.time()-t0:.1f}s")
