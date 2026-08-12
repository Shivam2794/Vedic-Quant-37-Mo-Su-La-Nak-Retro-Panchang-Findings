import os
import pyarrow.parquet as pq
from google.cloud import bigquery

PROJECT_ID    = "vedic-quant-442817"
DATASET_ID    = "feature_matrix"
TABLE_ID      = "stock_features_v2"
FEATURES_DIR  = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\features_partitioned"
# Using gcloud Application Default Credentials (gcloud auth application-default login)

NEW_TICKERS = ['SPY','QQQ','IWM','DIA','GLD','SLV','USO','TLT','XLE','VIXY']

client = bigquery.Client(project=PROJECT_ID)
table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"


# Find parquet files for new tickers
import glob

uploaded = 0
errors   = []

for ticker in NEW_TICKERS:
    # Partitioned dataset: features_partitioned/ticker=SPY/year=2024/*.parquet
    pattern = os.path.join(FEATURES_DIR, f"ticker={ticker}", "**", "*.parquet")
    files   = glob.glob(pattern, recursive=True)
    if not files:
        # Try non-partitioned pattern
        pattern2 = os.path.join(FEATURES_DIR, f"ticker={ticker}*.parquet")
        files = glob.glob(pattern2)
    if not files:
        print(f"  {ticker}: no parquet files found at {FEATURES_DIR}/ticker={ticker}/")
        continue

    print(f"  {ticker}: {len(files)} parquet files...")
    for fpath in files:
        try:
            df = pq.read_table(fpath).to_pandas()
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
                autodetect=True,
            )
            job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
            job.result()
            uploaded += len(df)
        except Exception as e:
            errors.append(f"{ticker}/{os.path.basename(fpath)}: {e}")

print(f"\nUploaded {uploaded:,} rows to BQ")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors[:5]:
        print(f"  {e}")
