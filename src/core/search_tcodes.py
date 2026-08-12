import os
import re

downloads_dir = r"C:\Users\Shivam Patel\Downloads"
transcripts = [f for f in os.listdir(downloads_dir) if f.endswith("_transcript.txt")]

tcode_regex = re.compile(r"\b[A-Za-z0-9_]{3,20}\b")

for t in transcripts:
    path = os.path.join(downloads_dir, t)
    print(f"\n=== Searching in {t} ===")
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        # look for typical SAP terminology or codes
        if any(term in line.lower() for term in ["t code", "t-code", "tcode", "y_", "z_", "kotg", "v_", "vk", "va", "me", "se", "override", "inclusion", "exclusion"]):
            print(f"Line {i+1}: {line.strip()}")
