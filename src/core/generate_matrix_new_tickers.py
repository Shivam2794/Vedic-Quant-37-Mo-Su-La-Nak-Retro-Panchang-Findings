"""
generate_matrix_new_tickers.py
Runs generate_matrix ONLY for the 10 new index/commodity/ETF tickers.
Outputs to the same partitioned dataset, so BQ upload will just add new partitions.
"""
import sys, time
sys.path.insert(0, r"C:\Users\Shivam Patel\Desktop\Python\Learn")
sys.path.insert(0, r"C:\Users\Shivam Patel\.gemini\antigravity\scratch")

import generate_matrix as gm

NEW_TICKERS = ['SPY','QQQ','IWM','DIA','GLD','SLV','USO','TLT','XLE','VIXY']

print("Initializing Generator Engine...")
engine = gm.StockAstroEngine()
rule_funcs = gm.load_compiled_rules()
print(f"Engine loaded {len(engine.natal_cache)} natal charts.")

sky_cache = {}
t_start = time.perf_counter()
total_rows = 0

for i, tk in enumerate(NEW_TICKERS):
    if tk not in engine.natal_cache:
        print(f"  [{tk}] Not in natal_cache, skipping")
        continue
    print(f"[{i+1}/{len(NEW_TICKERS)}] Processing {tk}...")
    rows = gm.process_ticker(tk, engine, rule_funcs, sky_cache)
    if rows:
        total_rows += rows
        print(f"  -> {rows} rows written")
    else:
        print(f"  -> 0 rows (check market data)")

elapsed = time.perf_counter() - t_start
print("=" * 50)
print(f"New ticker matrix generation complete")
print(f"Total rows: {total_rows}")
print(f"Time: {elapsed/60:.2f} min")
