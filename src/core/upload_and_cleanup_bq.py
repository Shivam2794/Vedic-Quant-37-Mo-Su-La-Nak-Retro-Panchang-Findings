"""
Robust BigQuery Uploader
Uploads generated parquet partitions to BigQuery and deletes local files on success.
"""
import os
import glob
import pyarrow.parquet as pq
from google.cloud import bigquery

PROJECT_ID    = "project-6cd52f66-6865-4de9-9af"
DATASET_ID    = "antigravity_quant"
TABLE_ID      = "feature_matrix"
FEATURES_DIR  = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\features_partitioned"

client = bigquery.Client(project=PROJECT_ID)
table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

# Find all ticker directories
ticker_dirs = glob.glob(os.path.join(FEATURES_DIR, "ticker=*"))

print(f"Found {len(ticker_dirs)} ticker directories to process.")

total_uploaded = 0
total_freed_mb = 0

for tdir in ticker_dirs:
    ticker = os.path.basename(tdir).split('=')[1]
    parquet_files = glob.glob(os.path.join(tdir, "**", "*.parquet"), recursive=True)
    
    if not parquet_files:
        continue
        
    print(f"Uploading {ticker} ({len(parquet_files)} files)...")
    
    ticker_uploaded = 0
    ticker_freed = 0
    
    for fpath in parquet_files:
        try:
            # Read to check rows
            import pandas as pd
            import re
            df = pq.read_table(fpath).to_pandas()
            
            # Fix pyarrow partition category types for BigQuery
            if 'ticker' in df.columns:
                df['ticker'] = pd.Series(df['ticker']).astype(str)
            if 'year' in df.columns:
                df['year'] = pd.Series(df['year']).astype('int32')
                
            # Fix BigQuery case-insensitive column duplicates and invalid chars
            def clean_col(c):
                s = str(c).lower().replace(' ', '_').replace('-', '_')
                return re.sub(r'[^a-z0-9_]', '', s)
            df.columns = [clean_col(c) for c in df.columns]
            df = df.loc[:, ~df.columns.duplicated()]
                
            rows = len(df)
            file_size_mb = os.path.getsize(fpath) / (1024 * 1024)
            
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
                autodetect=True,
            )
            job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
            job.result() # Wait for job to finish
            
            ticker_uploaded += rows
            ticker_freed += file_size_mb
            
            # Successfully uploaded, so DELETE the local file to save space
            os.remove(fpath)
            
        except Exception as e:
            print(f"  Error uploading {fpath}: {e}")
            
    total_uploaded += ticker_uploaded
    total_freed_mb += ticker_freed
    print(f"  -> {ticker_uploaded} rows uploaded, {ticker_freed:.1f} MB freed.")
    
print("=" * 50)
print(f"UPLOAD COMPLETE.")
print(f"Total Rows Uploaded: {total_uploaded:,}")
print(f"Total Space Freed: {total_freed_mb / 1024:.2f} GB")
