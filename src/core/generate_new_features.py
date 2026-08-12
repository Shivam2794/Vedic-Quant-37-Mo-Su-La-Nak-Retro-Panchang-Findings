"""
Phase 6A Step 3: Generate Feature Matrices for New Tickers
==========================================================
Uses the existing ephemeris_engine + transit_engine pipeline
but processes ONLY the new 86 tickers in batches of 10.
"""
import sys
import os
import gc
import time

sys.path.insert(0, r"C:\Users\Shivam Patel\.gemini\antigravity\scratch")

from generate_matrix import process_ticker, load_compiled_rules
from transit_engine import StockAstroEngine

OUTPUT_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\features_partitioned"

# All new tickers that need feature matrices
NEW_TICKERS = [
    "TSM", "AMD", "ASML", "INTC", "ADI", "NXPI", "MU",
    "PLTR", "HUBS", "TYL", "TRMB",
    "IBM", "CTSH", "EPAM", "DXC",
    "MTCH", "TRIP", "YELP", "IAC",
    "VZ", "T", "CMCSA", "TMUS",
    "BABA", "MELI", "EBAY", "ETSY", "M", "KSS", "DDS",
    "DG", "KR", "CASY", "BJ",
    "SQ", "FI", "FIS", "JKHY",
    "MCO", "MSCI", "CBOE", "FDS", "LPLA", "EVR",
    "GE", "RTX", "BA", "LMT", "GD", "TDG", "LHX", "AXON",
    "CAT", "CMI", "PCAR", "OSK", "WAB", "TTC", "TEX", "ALSN",
    "AGCO",
    "CSX", "JBHT", "SAIA", "R", "LSTR",
    "UPS", "FDX",
    "JNJ", "ABT",
    "XOM", "CVX",
    "CSGP", "CBRE",
    "APP", "HOOD", "HWM", "CPNG", "TOST", "AFRM", "GO", "CPAY",
    "DOX", "SNDR", "ARCB", "CARG",
]

def main():
    print("=" * 60, flush=True)
    print("PHASE 6A STEP 3: GENERATING FEATURE MATRICES", flush=True)
    print(f"Processing {len(NEW_TICKERS)} new tickers", flush=True)
    print("=" * 60, flush=True)
    
    # Skip tickers that already have features
    to_process = []
    for tk in NEW_TICKERS:
        tk_dir = os.path.join(OUTPUT_DIR, f"ticker={tk}")
        if os.path.exists(tk_dir):
            print(f"  [SKIP] {tk} (features already exist)", flush=True)
        else:
            to_process.append(tk)
    
    print(f"\n{len(to_process)} tickers need feature generation.", flush=True)
    
    if not to_process:
        print("All features already generated!", flush=True)
        return
    
    # Initialize engine
    print("Initializing Astro Engine...", flush=True)
    engine = StockAstroEngine()
    rule_funcs = load_compiled_rules()
    sky_cache = {}
    
    t_start = time.perf_counter()
    total_rows = 0
    
    for i, tk in enumerate(to_process):
        print(f"[{i+1}/{len(to_process)}] Processing {tk}...", flush=True)
        try:
            rows = process_ticker(tk, engine, rule_funcs, sky_cache)
            if rows:
                total_rows += rows
                print(f"  -> {rows} rows generated", flush=True)
            else:
                print(f"  -> SKIPPED (no data)", flush=True)
        except Exception as e:
            print(f"  -> ERROR: {e}", flush=True)
        
        # Memory management
        if (i + 1) % 5 == 0:
            gc.collect()
            elapsed = time.perf_counter() - t_start
            rate = (i + 1) / (elapsed / 60)
            remaining = (len(to_process) - i - 1) / rate if rate > 0 else 0
            print(f"  [Progress: {i+1}/{len(to_process)} | {elapsed/60:.1f}m elapsed | ~{remaining:.1f}m remaining]", flush=True)
    
    elapsed = time.perf_counter() - t_start
    print("\n" + "=" * 60, flush=True)
    print(f"FEATURE GENERATION COMPLETE", flush=True)
    print(f"Total Rows: {total_rows} | Time: {elapsed/60:.1f} mins", flush=True)
    print("=" * 60, flush=True)

if __name__ == "__main__":
    main()
