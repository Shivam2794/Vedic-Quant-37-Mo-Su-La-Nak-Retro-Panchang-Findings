import subprocess
import os

BQ_CMD = r"C:\Users\Shivam Patel\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd"
dest_table = "antigravity_quant.sector_sieve_results"
sql = f"""INSERT INTO `{dest_table}`
SELECT 'test_rule' AS rule_name, '1D' AS horizon, s.sector AS sector, COUNT(*) AS n_total, 1 AS n_active, 0.5 AS activation_rate, 0.0 AS mean_return_active, 0.0 AS mean_return_inactive, 0.0 AS differential_return, 0.0 AS std_return_active, 0.0 AS cost_adjusted_ir, 0.0 AS pearson_corr FROM `antigravity_quant.feature_matrix` f JOIN `antigravity_quant.stock_returns` r ON f.ticker = r.ticker AND DATE(f.date) = DATE(r.date) JOIN `antigravity_quant.sector_tags` s ON f.ticker = s.ticker GROUP BY s.sector"""

sql_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\test_batch.sql"
with open(sql_path, "w", encoding="utf-8") as f:
    f.write(sql)

res = subprocess.run(
    [BQ_CMD, "query", "--use_legacy_sql=false", "--nouse_cache", f"<{sql_path}"],
    shell=True, capture_output=True, text=True
)
print("Return code:", res.returncode)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
