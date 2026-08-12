import os
from pathlib import Path

path = Path(r"C:\Users\Shivam Patel\Downloads\Hedging ML plan.md")
print(f"Reading: {path}")
if not path.exists():
    print("File does not exist.")
else:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"Size: {len(content)} chars")
    lines = content.split('\n')
    print("Headers:")
    for l in lines:
        if l.startswith('#'):
            safe_l = l.encode('ascii', 'replace').decode('ascii')
            print(f"  {safe_l}")
            
    print("\n--- First 3000 chars ---")
    safe_text = content[:3000].encode('ascii', 'replace').decode('ascii')
    print(safe_text + ("\n... [TRUNCATED] ..." if len(content) > 3000 else ""))
