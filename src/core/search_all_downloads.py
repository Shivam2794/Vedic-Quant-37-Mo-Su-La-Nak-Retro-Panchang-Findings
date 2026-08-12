import os
import re
import zipfile

downloads_dir = r"C:\Users\Shivam Patel\Downloads"
targets = [
    "ssvi_calibrator",
    "intraday_interpolator",
    "microstructure_layer",
    "validation_suite",
    "anchor_generator",
    "gpu_historical_tick_generator",
    "run_massive_generation",
    "vix_anchor_generator",
    "run_massive_generation_parallel"
]

print("Scanning all downloads for pipeline code...")

for root, dirs, files in os.walk(downloads_dir):
    for file in files:
        fp = os.path.join(root, file)
        
        # Skip very large zips if we don't need them, but let's check text files first
        if file.endswith(".md") or file.endswith(".txt") or file.endswith(".py"):
            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                # Check for target files or class/def within the text
                for t in targets:
                    if t in content:
                        print(f"[FOUND KEYWORD] '{t}' in text file: {file}")
                        # Let's see if this contains code blocks with 'def '
                        if "def " in content or "class " in content:
                            print(f"  -> File {file} contains python definitions!")
            except Exception as e:
                pass
                
        elif file.endswith(".zip"):
            try:
                with zipfile.ZipFile(fp) as z:
                    for name in z.namelist():
                        for t in targets:
                            if t in name:
                                print(f"[FOUND IN ZIP] '{t}' in zip file: {file} -> {name}")
            except Exception as e:
                pass
