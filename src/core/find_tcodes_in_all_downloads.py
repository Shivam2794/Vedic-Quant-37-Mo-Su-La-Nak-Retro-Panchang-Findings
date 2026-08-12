import os
import re

downloads_dir = r"C:\Users\Shivam Patel\Downloads"
files = [f for f in os.listdir(downloads_dir) if f.endswith(".txt") or f.endswith(".md")]

patterns = [
    re.compile(r"\b(y_[a-za-z0-9_]+|z_[a-za-z0-9_]+)\b", re.IGNORECASE),
    re.compile(r"/[no][a-za-z0-9_]+", re.IGNORECASE),
    re.compile(r"\b(gcu[0-9]|se[0-9]+|vk[0-9]+|va[0-9]+|mm[0-9]+|kotg[0-9]*)\b", re.IGNORECASE)
]

print("Scanning all downloads text/markdown files for SAP T-codes...")

for fn in files:
    fp = os.path.join(downloads_dir, fn)
    try:
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            for idx, line in enumerate(f):
                for pat in patterns:
                    matches = pat.findall(line)
                    if matches:
                        print(f"[{fn}] L{idx+1}: {line.strip()} (Matched: {matches})")
    except Exception as e:
        pass
