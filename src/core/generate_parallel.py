import os, sys, time
import concurrent.futures

sys.path.insert(0, r'C:\Users\Shivam Patel\Desktop\Python\Learn')
sys.path.insert(0, r'C:\Users\Shivam Patel\.gemini\antigravity\scratch')

import generate_matrix as gm

NEW_TICKERS = ['SPY','QQQ','IWM','DIA','GLD','SLV','USO','TLT','XLE','VIXY']

# The worker function MUST initialize its own engine because sqlite3 connections can't be pickled.
def worker(tk):
    # Initialize engine locally inside the process
    engine = gm.StockAstroEngine()
    rule_funcs = gm.load_compiled_rules()
    sky_cache = {}
    return gm.process_ticker(tk, engine, rule_funcs, sky_cache)

if __name__ == '__main__':
    # Initialize engine once just to get the list of tickers
    dummy_engine = gm.StockAstroEngine()
    all_tickers = list(dummy_engine.natal_cache.keys())
    
    # We only want to process the original 155 stocks
    target_tickers = [t for t in all_tickers if t not in NEW_TICKERS]
    
    print(f"Targeting {len(target_tickers)} original tickers...")
    print(f"Processing in parallel across {os.cpu_count() - 1} cores...")
    
    t_start = time.perf_counter()
    total_rows = 0
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count() - 1) as executor:
        futures = {executor.submit(worker, tk): tk for tk in target_tickers}
        
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            tk = futures[future]
            try:
                rows = future.result()
                if rows:
                    total_rows += rows
                print(f"[{i+1}/{len(target_tickers)}] {tk} completed -> {rows or 0} rows")
            except Exception as e:
                print(f"[{i+1}/{len(target_tickers)}] {tk} FAILED: {e}")
                
    elapsed = time.perf_counter() - t_start
    print("="*50)
    print("MATRIX GENERATION COMPLETE")
    print(f"Total Rows Generated: {total_rows}")
    print(f"Total Time: {elapsed/60:.2f} mins")
