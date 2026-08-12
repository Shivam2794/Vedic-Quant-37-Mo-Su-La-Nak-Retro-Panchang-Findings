import os

scratch_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
files = [f for f in os.listdir(scratch_dir) if f.endswith(".txt") or f.endswith(".md")]

print("Searching all scratch text/markdown files for T-codes and compiled SAP findings...")

for fn in files:
    fp = os.path.join(scratch_dir, fn)
    found = []
    try:
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            for idx, line in enumerate(f):
                if any(term in line.lower() for term in ["t-code", "tcode", "kotg", "gcul", "gcu1", "pdp", "alteryx", "cartesian"]):
                    found.append((idx + 1, line.strip()))
        if found:
            print(f"\nFile: {fn} ({len(found)} matches)")
            for l_num, text in found[:10]:
                print(f"  L{l_num}: {text[:120]}")
            if len(found) > 10:
                print(f"  ... and {len(found) - 10} more matches ...")
    except Exception as e:
        print(f"Error reading {fn}: {e}")
