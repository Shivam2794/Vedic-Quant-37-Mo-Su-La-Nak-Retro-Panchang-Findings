import os
import re

downloads_dir = r"C:\Users\Shivam Patel\Downloads"
for fn in os.listdir(downloads_dir):
    if fn.endswith(".md") or fn.endswith(".txt"):
        fp = os.path.join(downloads_dir, fn)
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Let's search if it contains class or def of some options functions
        matches = re.findall(r"def\s+(?:bsm|ssvi|intraday|calibrate_ssvi|penny_pilot)", content)
        if matches:
            print(f"File {fn} has potential Python definitions: {matches}")
