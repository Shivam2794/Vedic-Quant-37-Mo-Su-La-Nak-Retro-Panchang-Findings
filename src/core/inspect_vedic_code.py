import re
from pathlib import Path

files = ["ephemeris_engine.py", "jaimini_master_pipeline.py", "nadi_master_pipeline.py", "transit_engine.py"]
scratch_dir = Path(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch")

for name in files:
    p = scratch_dir / name
    print(f"\n=======================================================")
    print(f"FILE: {name}")
    print(f"=======================================================")
    if not p.exists():
        print("File not found.")
        continue
        
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Extract imports, class names, function names, and comments
    lines = content.split('\n')
    
    # Let's extract functions and classes using simple regex
    classes = re.findall(r"class\s+(\w+)(?:\((.*?)\))?:", content)
    funcs = re.findall(r"def\s+(\w+)\((.*?)\):", content)
    
    print("Classes:")
    for c in classes:
        print(f"  - class {c[0]}({c[1]})")
        
    print("Functions:")
    for fn in funcs[:15]:
        print(f"  - def {fn[0]}({fn[1][:60]}...)")
        
    print("\n--- Code Header (first 60 lines) ---")
    safe_header = '\n'.join(lines[:60]).encode('ascii', 'replace').decode('ascii')
    print(safe_header)
