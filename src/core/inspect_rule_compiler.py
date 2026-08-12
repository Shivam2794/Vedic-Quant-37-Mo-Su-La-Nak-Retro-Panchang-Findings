import os
from pathlib import Path

files = ["rule_compiler.py", "rule_compiler_v2.py", "generate_new_features.py", "train_xgboost_triple_barrier.py"]
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
        
    lines = content.split('\n')
    
    # Classes & Functions
    import re
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
