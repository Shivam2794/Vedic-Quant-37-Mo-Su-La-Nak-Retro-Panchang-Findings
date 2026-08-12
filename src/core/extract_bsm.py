import os

downloads_dir = r"C:\Users\Shivam Patel\Downloads"
md_path = os.path.join(downloads_dir, "Synthesizing High-Accuracy Options Data 13.md")

with open(md_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

import sys
sys.stdout.reconfigure(encoding='utf-8')

for i, line in enumerate(lines):
    if "def bsm" in line or "class SSVI" in line or "class Intraday" in line:
        print(f"Match found at line {i+1}: {line.strip()}")
        # print 50 lines after it
        print("".join(lines[i:i+50]))
        print("="*80)

