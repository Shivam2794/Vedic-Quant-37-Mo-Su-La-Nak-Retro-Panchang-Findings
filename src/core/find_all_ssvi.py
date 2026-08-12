import os
import re

search_dirs = [
    r"C:\Users\Shivam Patel\.gemini\antigravity",
    r"C:\Users\Shivam Patel\Downloads",
    r"C:\Users\Shivam Patel\Desktop",
    r"C:\Users\Shivam Patel\Documents"
]

targets = ["ssvi_calibrator", "calibrate_ssvi", "IntradayInterpolator", "microstructure_layer", "gpu_historical_tick_generator"]

print("Starting deep search for pipeline code...")
for d in search_dirs:
    if not os.path.exists(d):
        continue
    print(f"Searching directory: {d}...")
    for root, dirs, files in os.walk(d):
        # Skip some standard directories to speed up
        if any(x in root for x in [".git", "__pycache__", "node_modules", "AppData"]):
            continue
        for file in files:
            fp = os.path.join(root, file)
            # Skip very large files
            try:
                size = os.path.getsize(fp)
                if size > 5 * 1024 * 1024:
                    continue
            except:
                continue
                
            if file.endswith((".py", ".md", ".txt", ".json", ".pkl")):
                try:
                    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    
                    found = []
                    for t in targets:
                        if t in content:
                            found.append(t)
                    if found:
                        print(f"  [MATCH] File: {fp} (size: {size} bytes) -> contains {found}")
                        # If it is a python file or contains class/def, print more details
                        if file.endswith(".py"):
                            print(f"    This is a python file! Let's examine it.")
                except Exception as e:
                    pass
print("Search finished.")
