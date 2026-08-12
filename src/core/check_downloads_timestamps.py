import os
from pathlib import Path
from datetime import datetime

downloads = Path(r"C:\Users\Shivam Patel\Downloads")
files = [f for f in downloads.iterdir() if f.is_file() and f.suffix == ".md"]

# Sort by last modification time descending
files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

print("Top 15 MD files in Downloads sorted by modification time:")
for idx, f in enumerate(files[:15], 1):
    mtime = datetime.fromtimestamp(f.stat().st_mtime)
    size = f.stat().st_size
    print(f"{idx}. {f.name:<60} | Size: {size/1024:>7.2f} KB | Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
