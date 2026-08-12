"""
Google Cloud Storage Parquet Streamer (Phase 1)
===============================================
Uploads the locally generated PyArrow partitioned Parquet matrix 
to a Google Cloud Storage bucket. This prepares the data for the 
distributed BigQuery Sieve while circumventing local memory limits.
"""
import os
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from google.cloud import storage
except ImportError:
    print("WARNING: google-cloud-storage is required. Run: pip install google-cloud-storage")

# Configuration
LOCAL_DATASET_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\features_partitioned"
GCP_BUCKET_NAME = "antigravity-quant-matrix"
GCP_PROJECT_ID = "project-6cd52f66-6865-4de9-9af"
MAX_WORKERS = 10 # Concurrent upload threads

def upload_file(bucket, local_path, destination_blob_name):
    """Uploads a single file to the bucket."""
    blob = bucket.blob(destination_blob_name)
    # Skip if already exists (resume capability)
    if blob.exists():
        return f"Skipped (Exists): {destination_blob_name}"
        
    blob.upload_from_filename(local_path)
    return f"Uploaded: {destination_blob_name}"

def upload_dataset():
    if not os.path.exists(LOCAL_DATASET_DIR):
        print(f"ERROR: Dataset directory not found: {LOCAL_DATASET_DIR}")
        return
        
    print("Initializing Google Cloud Storage Client...")
    try:
        # Assumes GOOGLE_APPLICATION_CREDENTIALS environment variable is set
        client = storage.Client(project=GCP_PROJECT_ID)
    except Exception as e:
        print(f"ERROR initializing GCS client: {e}")
        print("Ensure you have run: gcloud auth application-default login")
        return

    # Instantiate bucket directly
    bucket = client.bucket(GCP_BUCKET_NAME)

    # Find all parquet files
    search_pattern = os.path.join(LOCAL_DATASET_DIR, "**", "*.parquet")
    parquet_files = glob.glob(search_pattern, recursive=True)
    
    if not parquet_files:
        print("No Parquet files found in the dataset directory.")
        return
        
    print(f"Found {len(parquet_files)} Parquet partitions. Initiating threaded upload...")
    
    success_count = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}
        for local_path in parquet_files:
            # Preserve the partitioned directory structure in GCS 
            # e.g., features_partitioned\ticker=AAPL\year=2020\part-0.parquet
            # -> ticker=AAPL/year=2020/part-0.parquet
            rel_path = os.path.relpath(local_path, LOCAL_DATASET_DIR)
            blob_name = rel_path.replace(os.sep, "/")
            
            future = executor.submit(upload_file, bucket, local_path, blob_name)
            futures[future] = blob_name
            
        for future in as_completed(futures):
            try:
                result = future.result()
                print(result)
                success_count += 1
            except Exception as e:
                blob_name = futures[future]
                print(f"ERROR uploading {blob_name}: {e}")
                
    print("="*50)
    print("UPLOAD COMPLETE")
    print("="*50)
    print(f"Successfully processed {success_count}/{len(parquet_files)} files.")
    print(f"Destination: gs://{GCP_BUCKET_NAME}/")

if __name__ == "__main__":
    upload_dataset()
