import os
import glob
import time
from datetime import datetime
import subprocess

try:
    from google.cloud import storage
except ImportError:
    pass

TARGET_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\features_partitioned"
files = glob.glob(os.path.join(TARGET_DIR, "**", "*.parquet"), recursive=True)

cutoff = datetime(2026, 5, 1).timestamp()
deleted = 0
for f in files:
    if os.path.getmtime(f) < cutoff:
        os.remove(f)
        deleted += 1

print(f"Deleted {deleted} old parquet files locally.")

# Also purge from GCS to ensure clean load
print("Purging GCS bucket to ensure clean load...")
subprocess.run(r"C:\Users\Shivam Patel\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gsutil.cmd -m rm -r gs://antigravity-quant-matrix/*", shell=True)
print("GCS Purge complete.")
