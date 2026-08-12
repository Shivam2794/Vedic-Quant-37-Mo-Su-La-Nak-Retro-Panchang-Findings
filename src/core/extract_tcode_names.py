import os
import re

downloads_dir = r"C:\Users\Shivam Patel\Downloads"
transcripts = sorted([f for f in os.listdir(downloads_dir) if f.endswith("_transcript.txt")])

print("Scanning for T-codes and exclusion analysis...")

for fn in transcripts:
    fp = os.path.join(downloads_dir, fn)
    with open(fp, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if "exclusion analysis" in line.lower() or "upload" in line.lower() or "t-code" in line.lower() or "tcode" in line.lower():
                # Let's print the line and the next 2 lines
                print(f"[{fn}] L{idx+1}: {line.strip()}")
