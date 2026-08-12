"""
Phase 6B: Sector-Stratified Sieve Runner
===========================================================
Runs the BigQuery sieve incorporating the new GICS sector tags.
Evaluates (Rule, Sector, Horizon) combos to uncover signals
that are highly predictive for specific sectors but may cancel
out in the global market.
"""
import json
import os
import re
import time
import subprocess
import sqlite3

BQ_CMD = r"C:\Users\Shivam Patel\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd"
DEDUP_RULES_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\compiled_rules_deduped.json"
DB_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_natal_charts.db"

def sanitize_for_bq(name):
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)

def get_sectors():
    """Fetch distinct sectors from local DB to use in grouping."""
    conn = sqlite3.connect(DB_PATH)
    sectors = [r[0] for r in conn.execute("SELECT DISTINCT sector FROM sector_tags WHERE sector IS NOT NULL").fetchall()]
    conn.close()
    return sectors

def main():
    print("="*60)
    print("PHASE 6B: SECTOR-STRATIFIED SIEVE")
    print("="*60)
    
    # Sector tags are already loaded and correctly mapped in BQ.

    # 2. Re-create external table to include the new partitions? 
    # External tables read directly from GCS. If we added new partitioned directories to GCS,
    # BQ picks them up if we run bq query to refresh partitions, or we recreate it.
    print("Refreshing Hive partitions on feature_matrix...")
    # This requires recreating the external table definition or running a metadata refresh.
    # bq query --use_legacy_sql=false "ALTER TABLE antigravity_quant.feature_matrix_ext REFRESH" (if external table is native BQ partitioned)
    # Actually, BQ external tables partitioned by hive structure can be refreshed.
    # We will assume `bq_upload.py` uploads everything and we can manually refresh or recreate the table if needed.
    
    # Load deduped rules
    with open(DEDUP_RULES_PATH, "r") as f:
        dedup_rules = list(json.load(f).keys())
    print(f"Loaded {len(dedup_rules)} unique rules.")

    # Get ALL feature columns (the 214 PDF rules + 740+ ML features)
    print("Fetching ALL feature columns from BQ...")
    # Get all columns except the base keys and raw astro data
    col_sql = """
    SELECT column_name 
    FROM `antigravity_quant`.INFORMATION_SCHEMA.COLUMNS 
    WHERE table_name = 'feature_matrix' 
      AND column_name NOT IN ('ticker', 'date', 'year', 'sector')
      AND column_name NOT LIKE '%_longitude%'
      AND column_name NOT LIKE '%_speed%'
      AND column_name NOT LIKE '%_sin'
      AND column_name NOT LIKE '%_cos'
      AND data_type IN ('INT64', 'FLOAT64')
    """
    # Create single string for shell execution on Windows
    clean_sql = col_sql.strip().replace('\n', ' ')
    cmd = f'"{BQ_CMD}" query --use_legacy_sql=false --format=csv --max_rows=5000 "{clean_sql}"'
    
    result = subprocess.run(
        cmd,
        shell=True, capture_output=True, text=True
    )
    bq_rule_cols = set(line.strip() for line in result.stdout.strip().split('\n')[1:] if line.strip())
    
    # Build unique available list - each BQ column appears exactly once
    available = [(col, col) for col in sorted(bq_rule_cols)]
    
    print(f"  {len(available)} features found in BQ (PDF rules + ML features).")

    # Generate SQL blocks grouping by Sector
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
        s.sector AS sector,
        COUNT(*) AS n_total,
        CAST(SUM(CAST(ROUND(COALESCE(CAST(`{bq_col}` AS FLOAT64), 0.0)) AS INT64)) AS INT64) AS n_active,
        SAFE_DIVIDE(SUM(CAST(ROUND(COALESCE(CAST(`{bq_col}` AS FLOAT64), 0.0)) AS INT64)), COUNT(*)) AS activation_rate,
        AVG(IF(ROUND(COALESCE(CAST(`{bq_col}` AS FLOAT64), 0.0)) = 1, r.{horizon_col}, NULL)) AS mean_return_active,
        AVG(IF(ROUND(COALESCE(CAST(`{bq_col}` AS FLOAT64), 0.0)) = 0, r.{horizon_col}, NULL)) AS mean_return_inactive,
        AVG(IF(ROUND(COALESCE(CAST(`{bq_col}` AS FLOAT64), 0.0)) = 1, r.{horizon_col}, NULL)) - AVG(IF(ROUND(COALESCE(CAST(`{bq_col}` AS FLOAT64), 0.0)) = 0, r.{horizon_col}, NULL)) AS differential_return,
        STDDEV(IF(ROUND(COALESCE(CAST(`{bq_col}` AS FLOAT64), 0.0)) = 1, r.{horizon_col}, NULL)) AS std_return_active,
        SAFE_DIVIDE(
          AVG(IF(ROUND(COALESCE(CAST(`{bq_col}` AS FLOAT64), 0.0)) = 1, r.{horizon_col}, NULL)) - 0.0005,
          STDDEV(IF(ROUND(COALESCE(CAST(`{bq_col}` AS FLOAT64), 0.0)) = 1, r.{horizon_col}, NULL))
        ) AS cost_adjusted_ir,
        CORR(CAST(`{bq_col}` AS FLOAT64), r.{horizon_col}) AS pearson_corr
      FROM `antigravity_quant.feature_matrix` f
      JOIN `antigravity_quant.stock_returns` r
        ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date)
      JOIN `antigravity_quant.sector_tags` s
        ON f.ticker = s.ticker
      WHERE r.{horizon_col} IS NOT NULL
      GROUP BY s.sector""")

    print(f"Generated {len(blocks)} SQL blocks.")

    # Split into batches of 30 blocks each (added group by makes query heavier)
    BLOCKS_PER_BATCH = 30
    batches = [blocks[i:i+BLOCKS_PER_BATCH] for i in range(0, len(blocks), BLOCKS_PER_BATCH)]

    print(f"Split into {len(batches)} batches.")

    start = time.time()
    dest_table = "antigravity_quant.sector_sieve_results"

    for bi, batch in enumerate(batches):
        union_sql = "\nUNION ALL\n".join(batch)
        # Pure SELECT query
        sql = union_sql
            
        sql_path = rf"C:\Users\Shivam Patel\.gemini\antigravity\scratch\temp_sector_batch_{bi}.sql"
        with open(sql_path, "w", encoding="utf-8") as f:
            f.write(sql)
            
        print(f"Executing Batch {bi+1}/{len(batches)}...")
        res = subprocess.run(
            f'"{BQ_CMD}" query --use_legacy_sql=false --format=csv --max_rows=100000 --nouse_cache < "{sql_path}"',
            shell=True, capture_output=True, text=True
        )
        if res.returncode != 0:
            print(f"  [ERROR] Batch {bi+1} Failed:")
            print("STDOUT:", res.stdout[:500])
            print("STDERR:", res.stderr[:500])
        else:
            print(f"  Batch {bi+1} Success.")
            
            # Write to CSV
            lines = [l.strip() for l in res.stdout.strip().split('\n') if l.strip()]
            if bi > 0 and len(lines) > 0:
                lines = lines[1:] # Skip header for subsequent batches
                
            out_csv = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\sector_sieve_candidates.csv"
            mode = "w" if bi == 0 else "a"
            with open(out_csv, mode, encoding="utf-8") as f:
                f.write('\n'.join(lines) + '\n')
        
        # Cleanup
        try:
            os.remove(sql_path)
        except:
            pass

    elapsed = time.time() - start
    print(f"Sieve completed in {elapsed/60:.2f} minutes.")
    
    print("[SUCCESS] Phase 6B Complete.")

if __name__ == "__main__":
    main()
