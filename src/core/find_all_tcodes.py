import os
import re

downloads_dir = r"C:\Users\Shivam Patel\Downloads"
transcripts = sorted([f for f in os.listdir(downloads_dir) if f.endswith("_transcript.txt")])

# Custom pattern for SAP transaction codes
# E.g., GCU1, GCUL, SE16, VK11, VA01, MM01, KOTG, /n..., /o...
# And custom codes starting with Z or Y
tcode_pattern = re.compile(r"\b(gcu[0-9a-zA-Z]|se[0-9a-zA-Z]{1,3}|vk[0-9a-zA-Z]{1,2}|va[0-9a-zA-Z]{1,2}|mm[0-9a-zA-Z]{1,2}|kotg[0-9]*|y_[a-zA-Z0-9_]+|z_[a-zA-Z0-9_]+)\b", re.IGNORECASE)
command_pattern = re.compile(r"/[no][a-zA-Z0-9_]+", re.IGNORECASE)

print("Scanning transcripts for SAP T-codes and command shortcuts...")

for t in transcripts:
    path = os.path.join(downloads_dir, t)
    print(f"\nScanning {t}...")
    found = []
    with open(path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            # Check T-codes
            m1 = tcode_pattern.findall(line)
            m2 = command_pattern.findall(line)
            matches = list(set(m1 + m2))
            if matches:
                found.append((idx + 1, line.strip(), matches))
                
    if found:
        print(f"Found {len(found)} references:")
        for l_num, text, matches in found[:15]: # Print first 15 references
            print(f"  L{l_num} (Matches: {matches}): {text[:100]}")
        if len(found) > 15:
            print(f"  ... and {len(found) - 15} more references ...")
    else:
        print("  No references found.")
