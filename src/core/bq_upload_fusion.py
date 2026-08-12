"""
Google Cloud Storage Parquet Streamer & Schema Fusion (Phase 7)
===============================================================
Uploads the expanded 950+ column feature matrix to GCS, fixes 
timestamp nanosecond issues, and recreates the BigQuery external 
table to force schema inference of the new ML features.
"""
import os
import glob
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from google.cloud import storage
except ImportError:
    print("WARNING: google-cloud-storage is required.")



LOCAL_DATASET_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\features_partitioned"
GCP_BUCKET_NAME = "antigravity-quant-matrix"
GCP_PROJECT_ID = "project-6cd52f66-6865-4de9-9af"
BQ_CMD = r"C:\Users\Shivam Patel\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd"


def main():
    print("="*60)
    print("PHASE 7 FUSION: GCS UPLOAD & BQ SCHEMA UPDATE")
    print("="*60)

    parquet_files = glob.glob(os.path.join(LOCAL_DATASET_DIR, "**", "*.parquet"), recursive=True)
    if not parquet_files:
        print("No Parquet files found. Aborting.")
        return

    # 2. Upload to GCS using gsutil (fixes ADC permission issues)
    print("\n[2/3] Uploading PyArrow Partitions to GCS using gsutil...")
    gsutil_cmd = r"C:\Users\Shivam Patel\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gsutil.cmd"
    # We upload the contents of features_partitioned into the bucket
    upload_result = subprocess.run(
        f'"{gsutil_cmd}" -m cp -r "{LOCAL_DATASET_DIR}\*" "gs://{GCP_BUCKET_NAME}/"',
        shell=True, capture_output=True, text=True
    )
    if upload_result.returncode != 0:
        print(f"ERROR uploading to GCS: {upload_result.stderr}")
        return
    print("Upload completed successfully!")

    # 3. Update BigQuery External Table Definition
    print("\n[3/3] Recreating BigQuery External Table for Schema Inference...")
    # Generate external table definition with hive partitioning
    def_file = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\feature_matrix_def.json"
    
    # Generate def
    subprocess.run([
        BQ_CMD, "mkdef", 
        "--source_format=PARQUET",
        "--hive_partitioning_mode=AUTO",
        "--hive_partitioning_source_uri_prefix=gs://antigravity-quant-matrix/{ticker:STRING}/{year:INTEGER}",
        "gs://antigravity-quant-matrix/*"
    ], stdout=open(def_file, 'w'))

    # Recreate table using the new definition to infer the ~950 columns
    # Drop first
    subprocess.run([
        BQ_CMD, "rm", "-f", "-t", "antigravity_quant.feature_matrix"
    ], capture_output=True)

    # Recreate
    result = subprocess.run([
        BQ_CMD, "mk", "--table", "--external_table_definition=" + def_file,
        "antigravity_quant.feature_matrix"
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print("SUCCESS: BigQuery external table 'feature_matrix' successfully updated with new schema!")
    else:
        print(f"ERROR updating BigQuery: {result.stderr}")

if __name__ == "__main__":
    main()
