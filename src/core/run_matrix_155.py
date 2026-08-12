
import sys, time, os
sys.path.insert(0, r'C:\Users\Shivam Patel\Desktop\Python\Learn')
sys.path.insert(0, r'C:\Users\Shivam Patel\.gemini\antigravity\scratch')
import generate_matrix as gm
import concurrent.futures

engine = gm.StockAstroEngine()
rule_funcs = gm.load_compiled_rules()
NEW_TICKERS = ['SPY','QQQ','IWM','DIA','GLD','SLV','USO','TLT','XLE','VIXY']
target_tickers = [t for t in engine.natal_cache.keys() if t not in NEW_TICKERS]

print(f'Processing {len(target_tickers)} tickers in parallel...')
t_start = time.perf_counter()
total_rows = 0

with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count() - 1) as executor:
    futures = {
        executor.submit(gm.process_ticker, tk, engine, rule_funcs, {}): tk 
        for tk in target_tickers
    }
    for i, future in enumerate(concurrent.futures.as_completed(futures)):
        tk = futures[future]
        try:
            rows_processed = future.result()
            if rows_processed:
                total_rows += rows_processed
            print(f'[{i+1}/{len(target_tickers)}] {tk} completed -> {rows_processed or 0} rows')
        except Exception as exc:
            print(f'[{i+1}/{len(target_tickers)}] {tk} generated an exception: {exc}')

elapsed = time.perf_counter() - t_start
print(f'Total Rows Generated: {total_rows}')
print(f'Total Time: {elapsed/60:.2f} mins')
