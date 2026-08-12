
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os
import gc

def initialize_output_directory(output_dir=r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\master_output"):
    """Ensures the Parquet output directory exists."""
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def save_asset_matrix(ticker, df, output_dir=r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\master_output"):
    """
    Saves the entire DataFrame as a Parquet file.
    TRAP P2.11 FIX: Removed 'row_group_size=len(df)'. 
    We now allow PyArrow to use its default row group chunking (typically 64MB) 
    to prevent monolithic 1.4GB memory spikes during XGBoost ingestion.
    """
    output_dir = initialize_output_directory(output_dir)
    file_path = os.path.join(output_dir, f"{ticker}_master.parquet")
    
    print(f"[{ticker}] Initializing chunked PyArrow Parquet dump...")
    
    chunk_size = 250000
    schema = pa.Schema.from_pandas(df)
    
    with pq.ParquetWriter(file_path, schema, compression='snappy') as writer:
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i : i + chunk_size]
            table = pa.Table.from_pandas(chunk, schema=schema)
            writer.write_table(table)
            del chunk
            del table
            
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    print(f"[{ticker}] Successfully sealed Parquet file: {file_path}")
    print(f"[{ticker}] Final Disk Size: {file_size_mb:.2f} MB")
    
    gc.collect()

def load_asset_matrix(ticker, output_dir=r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\master_output"):
    """Loads the Parquet file into memory."""
    file_path = os.path.join(output_dir, f"{ticker}_master.parquet")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Matrix for {ticker} not found at {file_path}")
    return pd.read_parquet(file_path, engine='pyarrow')
