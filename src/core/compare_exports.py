import os
from pathlib import Path

downloads = Path(r"C:\Users\Shivam Patel\Downloads")
f1 = downloads / "Antigravity_Chat_Export.md"
f2 = downloads / "Antigravity_V4_Chat_Export.md"

if not f1.exists() or not f2.exists():
    print("One or both files do not exist.")
else:
    with open(f1, "r", encoding="utf-8") as file1:
        c1 = file1.read()
    with open(f2, "r", encoding="utf-8") as file2:
        c2 = file2.read()
        
    print(f"File 1 (Antigravity_Chat_Export.md) size: {len(c1)} chars")
    print(f"File 2 (Antigravity_V4_Chat_Export.md) size: {len(c2)} chars")
    
    # Check if File 1's content is completely contained in File 2
    # Since File 2 might have edits, let's check unique paragraphs/sections
    # Let's extract all headings in both and see which ones in f1 are NOT in f2
    lines1 = c1.split('\n')
    lines2 = c2.split('\n')
    
    h1 = [l.strip() for l in lines1 if l.strip().startswith('#')]
    h2 = [l.strip() for l in lines2 if l.strip().startswith('#')]
    
    print(f"Total headings in File 1: {len(h1)}")
    print(f"Total headings in File 2: {len(h2)}")
    
    unique_to_f1 = [h for h in h1 if h not in h2]
    print(f"Headings unique to File 1: {len(unique_to_f1)}")
    for h in unique_to_f1[:20]:
        print(f"  - {h.encode('ascii', 'replace').decode('ascii')}")
