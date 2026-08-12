import os
import re

downloads_dir = r"C:\Users\Shivam Patel\Downloads"
files_to_check = [
    "Synthesizing High-Accuracy Options Data 13.md",
    "Synthesizing High-Accuracy Options Data 12.md",
    "Synthesizing High-Accuracy Options Data 11.md",
    "Synthesizing High-Accuracy Options Data 2.md",
    "Synthesizing High-Accuracy Options Data.md",
    "Scraper strategy.md"
]

print("Scanning for code blocks...")
for fn in files_to_check:
    fp = os.path.join(downloads_dir, fn)
    if not os.path.exists(fp):
        continue
    print(f"\n--- Checking file: {fn} ---")
    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Let's search for python code blocks or mentions of files
    for py_file in ["ssvi_calibrator", "intraday_interpolator", "microstructure_layer", 
                    "validation_suite", "anchor_generator", "gpu_historical_tick_generator", 
                    "run_massive_generation", "compare_real_vs_synthetic", "run_massive_generation_parallel", "vix_anchor_generator"]:
        count = len(re.findall(py_file, content, re.IGNORECASE))
        print(f"  {py_file}: {count} occurrences")
