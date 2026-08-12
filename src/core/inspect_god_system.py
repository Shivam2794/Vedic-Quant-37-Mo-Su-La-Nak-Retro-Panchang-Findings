import os
from pathlib import Path

god_dir = Path(r"C:\Users\Shivam Patel\.\.gemini\antigravity\scratch\ml_options_hedging_project\god_system")

print("Files in god_system recursively:")
for root, dirs, files in os.walk(god_dir):
    for f in files:
        p = Path(root) / f
        rel = p.relative_to(god_dir)
        size = p.stat().st_size
        print(f"  - {str(rel):<50} | Size: {size/1024:>7.2f} KB")
