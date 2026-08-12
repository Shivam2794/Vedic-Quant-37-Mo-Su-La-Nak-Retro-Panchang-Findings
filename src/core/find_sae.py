import os
import glob
import json

scratch_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
matches = []
for root, dirs, files in os.walk(scratch_dir):
    for f in files:
        if "ml_sae" in f:
            matches.append(os.path.join(root, f))
        
print("Found files:", matches)
with open(os.path.join(scratch_dir, "found_sae.txt"), "w") as out:
    for m in matches:
        out.write(m + "\n")
