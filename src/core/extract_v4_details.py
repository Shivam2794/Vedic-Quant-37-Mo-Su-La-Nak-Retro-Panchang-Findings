import os
from pathlib import Path

path = Path(r"C:\Users\Shivam Patel\Downloads\Antigravity_V4_Chat_Export.md")
if not path.exists():
    print("File does not exist.")
else:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    lines = content.split('\n')
    print(f"Total Lines: {len(lines)}")
    
    sections = [
        ("V5 TOP CHAMPIONS", 3370, 3430),
        ("V6 BUG FOUND", 3420, 3460),
        ("THE BUG I FOUND", 9680, 9730),
        ("THE TRUE V4 PERFORMANCE", 9820, 9870),
        ("FINAL AUTO-MEDIC & TASK SCHEDULER", 10540, 10760)
    ]
    
    for name, start, end in sections:
        print(f"\n=======================================================")
        print(f"SECTION: {name} (Lines {start}-{end})")
        print(f"=======================================================")
        
        # Slice lines (0-indexed, so subtract 1)
        slice_lines = lines[max(0, start-1):min(len(lines), end)]
        slice_text = '\n'.join(slice_lines)
        
        # Replace non-ascii chars to avoid print crashes
        safe_text = slice_text.encode('ascii', 'replace').decode('ascii')
        print(safe_text)
