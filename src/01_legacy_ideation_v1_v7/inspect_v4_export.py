import os
from pathlib import Path

path = Path(r"C:\Users\Shivam Patel\Downloads\Antigravity_V4_Chat_Export.md")
if not path.exists():
    print("File does not exist.")
else:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"Size: {len(content)} chars")
    lines = content.split('\n')
    print("Headings:")
    for idx, l in enumerate(lines):
        if l.startswith('#'):
            safe_l = l.encode('ascii', 'replace').decode('ascii')
            print(f"  Line {idx+1}: {safe_l}")
