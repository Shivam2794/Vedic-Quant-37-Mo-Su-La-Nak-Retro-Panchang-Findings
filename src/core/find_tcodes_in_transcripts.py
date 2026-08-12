import os
import re

downloads_dir = r"C:\Users\Shivam Patel\Downloads"
transcripts = sorted([f for f in os.listdir(downloads_dir) if f.endswith("_transcript.txt")])

# Search for common SAP T-codes:
# 1. Custom transaction codes starting with Y_ or Z_
# 2. Command line commands like /n... or /o...
# 3. Standard SAP transaction codes like SE11, SE16, SE16N, VK11, VK12, VA01, etc.
# 4. Words of 3-10 characters in uppercase that look like a transaction code (e.g., GCU1, KOTG)
# Let's write a regular expression that matches custom Y_ or Z_ codes, standard codes, or command line inputs.
patterns = [
    re.compile(r"\b(y_[a-za-z0-9_]+|z_[a-za-z0-9_]+)\b", re.IGNORECASE),
    re.compile(r"/[no][a-za-z0-9_]+", re.IGNORECASE),
    re.compile(r"\b(gcu[0-9]|se[0-9]+|vk[0-9]+|va[0-9]+|mm[0-9]+|kotg[0-9]*)\b", re.IGNORECASE),
    re.compile(r"\b([A-Z]{3,6}[0-9]{1,4}[A-Z]*|[A-Z]{1,4}[0-9]{3,6}[A-Z]*)\b")
]

print("Scanning all transcripts for potential SAP transaction codes...")

found_any = False
for t in transcripts:
    path = os.path.join(downloads_dir, t)
    with open(path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            for pat in patterns:
                matches = pat.findall(line)
                if matches:
                    print(f"[{t}] L{idx+1}: {line.strip()} (Matched: {matches})")
                    found_any = True

if not found_any:
    print("No direct T-code pattern matches found.")
