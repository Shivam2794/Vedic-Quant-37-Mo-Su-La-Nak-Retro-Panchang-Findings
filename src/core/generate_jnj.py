import sys, os
sys.path.insert(0, r'C:\Users\Shivam Patel\Desktop\Python\Learn')
sys.path.insert(0, r'C:\Users\Shivam Patel\.gemini\antigravity\scratch')
import generate_matrix as gm

print("Initializing Generator Engine for JNJ...")
engine = gm.StockAstroEngine()
rule_funcs = gm.load_compiled_rules()
sky_cache = {}

ticker = "JNJ"
print(f"Generating data for {ticker}...")
try:
    rows = gm.process_ticker(ticker, engine, rule_funcs, sky_cache)
    print(f"Success! {rows} rows generated for {ticker}.")
except Exception as e:
    print(f"Failed to generate for {ticker}: {e}")
