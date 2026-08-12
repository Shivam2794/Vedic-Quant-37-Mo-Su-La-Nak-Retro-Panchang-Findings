import sys
sys.path.append(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch")
from generate_matrix import process_ticker, load_compiled_rules
from transit_engine import StockAstroEngine
import pyarrow.parquet as pq
import os
import glob
import shutil

engine = StockAstroEngine()
rule_funcs = load_compiled_rules()
sky_cache = {}

existing = glob.glob(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\features_partitioned\ticker=NVDA")
if existing:
    shutil.rmtree(existing[0])

print("Running NVDA...")
process_ticker("NVDA", engine, rule_funcs, sky_cache)

files = glob.glob(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\features_partitioned\ticker=NVDA\*\*.parquet")
if files:
    df = pq.read_table(files[0]).to_pandas()
    print(f"Columns in NVDA parquet: {len(df.columns)}")
    print(f"Total Rows: {len(df)}")
else:
    print("No partition files found for NVDA")
