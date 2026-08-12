"""
BigQuery Statistical Sieve (Phase 1.7) — Batched Execution
===========================================================
Splits the 1070 SQL blocks into batches that fit within BQ's 1MB query limit.
Each batch writes results to a materialized table, then we read the final output.
"""
import json
import os
import re
import time
import subprocess
import math

BQ_CMD = r"C:\Users\Shivam Patel\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd"
DEDUP_RULES_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\compiled_rules_deduped.json"
OUTPUT_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\sieve_candidates.csv"

def sanitize_for_bq(name):
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)

# Load deduped rules
with open(DEDUP_RULES_PATH, "r") as f:
    dedup_rules = list(json.load(f).keys())
print(f"Loaded {len(dedup_rules)} unique rules.")

# Get BQ rule columns
print("Fetching feature_matrix columns from BQ...")
col_sql = "SELECT column_name FROM `antigravity_quant`.INFORMATION_SCHEMA.COLUMNS WHERE table_name = 'feature_matrix' AND column_name LIKE 'rule_%'"
result = subprocess.run(
    [BQ_CMD, "query", "--use_legacy_sql=false", "--format=csv", "--max_rows=1000", col_sql],
    capture_output=True, text=True
)
bq_rule_cols = set(line.strip() for line in result.stdout.strip().split('\n')[1:] if line.strip())
print(f"  BQ has {len(bq_rule_cols)} rule columns.")

# Match
available = []
for rule_name in dedup_rules:
    bq_col = f"rule_{sanitize_for_bq(rule_name)}"
    if bq_col in bq_rule_cols:
        available.append((rule_name, bq_col))
print(f"  {len(available)} deduped rules matched.")

# Generate SQL blocks
horizons = [
    ('fwd_return_1d', '1D'),
    ('fwd_return_5d', '5D'),
    ('fwd_return_10d', '10D'),
    ('fwd_return_21d', '21D'),
    ('fwd_return_63d', '63D'),
]

blocks = []
for rule_name, bq_col in available:
    safe_name = rule_name.replace("'", "\\'")
    for horizon_col, horizon_label in horizons:
        blocks.append(f"""SELECT
    '{safe_name}' AS rule_name,
    '{horizon_label}' AS horizon,
    COUNT(*) AS n_total,
    CAST(SUM(CAST(`{bq_col}` AS INT64)) AS INT64) AS n_active,
    SAFE_DIVIDE(SUM(CAST(`{bq_col}` AS INT64)), COUNT(*)) AS activation_rate,
    AVG(IF(`{bq_col}` = 1, r.{horizon_col}, NULL)) AS mean_return_active,
    AVG(IF(`{bq_col}` = 0, r.{horizon_col}, NULL)) AS mean_return_inactive,
    AVG(IF(`{bq_col}` = 1, r.{horizon_col}, NULL)) - AVG(IF(`{bq_col}` = 0, r.{horizon_col}, NULL)) AS differential_return,
    STDDEV(IF(`{bq_col}` = 1, r.{horizon_col}, NULL)) AS std_return_active,
    SAFE_DIVIDE(
      AVG(IF(`{bq_col}` = 1, r.{horizon_col}, NULL)) - 0.0005,
      STDDEV(IF(`{bq_col}` = 1, r.{horizon_col}, NULL))
    ) AS cost_adjusted_ir,
    CORR(CAST(`{bq_col}` AS FLOAT64), r.{horizon_col}) AS pearson_corr
  FROM `antigravity_quant.feature_matrix` f
  JOIN `antigravity_quant.stock_returns` r
    ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
  WHERE r.{horizon_col} IS NOT NULL""")

print(f"Generated {len(blocks)} SQL blocks.")

# Split into batches of 50 blocks each (BQ can't plan 700+ UNION ALLs)
BLOCKS_PER_BATCH = 50
batches = [blocks[i:i+BLOCKS_PER_BATCH] for i in range(0, len(blocks), BLOCKS_PER_BATCH)]

print(f"Split into {len(batches)} batches.")

# Execute batches
# First batch: CREATE OR REPLACE TABLE
# Subsequent batches: INSERT INTO
start = time.time()
dest_table = "antigravity_quant.sieve_results"

for bi, batch in enumerate(batches):
    union_sql = "\nUNION ALL\n".join(batch)
    
    if bi == 0:
        # Create destination table
        sql = f"""CREATE OR REPLACE TABLE `{dest_table}` AS
{union_sql}"""
    else:
        sql = f"""INSERT INTO `{dest_table}`
{union_sql}"""
    
    sql_file = rf"C:\Users\Shivam Patel\.gemini\antigravity\scratch\bq_sieve_batch_{bi}.sql"
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(sql)
    
    sql_kb = os.path.getsize(sql_file) / 1024
    print(f"  Batch {bi+1}/{len(batches)}: {len(batch)} blocks, {sql_kb:.0f} KB... ", end="", flush=True)
    
    with open(sql_file, "r", encoding="utf-8") as f:
        sql_content = f.read()
    
    result = subprocess.run(
        [BQ_CMD, "query", "--use_legacy_sql=false", "--format=csv", "--max_rows=0"],
        input=sql_content, capture_output=True, text=True, timeout=600
    )
    
    if result.returncode != 0:
        print(f"FAILED!")
        print(f"  Error: {result.stdout[:300]}")
        print(f"  Stderr: {result.stderr[:300]}")
        exit(1)
    
    print("OK")

# Query final results with filtering
print(f"\nQuerying filtered results from {dest_table}...")
filter_sql = f"""SELECT *
FROM `{dest_table}`
WHERE activation_rate BETWEEN 0.01 AND 0.50
  AND n_active >= 20
  AND (ABS(differential_return) > 0.003 OR ABS(pearson_corr) > 0.015)
ORDER BY cost_adjusted_ir DESC"""

result = subprocess.run(
    [BQ_CMD, "query", "--use_legacy_sql=false", "--format=csv", "--max_rows=10000", filter_sql],
    capture_output=True, text=True, timeout=120
)

elapsed = time.time() - start

if result.returncode != 0:
    print(f"ERROR: {result.stdout[:500]}")
    exit(1)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(result.stdout)

lines = result.stdout.strip().split('\n')
n_results = len(lines) - 1

print(f"\n{'='*60}")
print(f"SIEVE COMPLETE (Took {elapsed:.1f}s on BigQuery)")
print(f"{'='*60}")
print(f"Candidates surviving sieve: {n_results}")
print(f"Output: {OUTPUT_PATH}")
print(f"\nTop 20 results:")
for line in lines[:21]:
    print(line)
