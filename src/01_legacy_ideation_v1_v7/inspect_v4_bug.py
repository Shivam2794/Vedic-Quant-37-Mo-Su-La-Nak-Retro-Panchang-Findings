import os
from pathlib import Path

path = Path(r"C:\Users\Shivam Patel\.gemini\antigravity\brain\879cc675-1bac-47f1-9b56-8c074e27bd91\v4_options_hedging_latest_learnings.md")
if not path.exists():
    print("File not found.")
else:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    lines = content.split('\n')
    
    # Search for the lines that contain "THE BUG I FOUND"
    for idx, l in enumerate(lines):
        if "THE BUG I FOUND" in l:
            print(f"Found at line {idx+1}")
            start = max(0, idx - 5)
            end = min(len(lines), idx + 100)
            
            slice_lines = lines[start:end]
            slice_text = '\n'.join(slice_lines)
            safe_text = slice_text.encode('ascii', 'replace').decode('ascii')
            print(safe_text)
            break
