import json
from pathlib import Path

# Load export
export_path = Path(r"C:\Users\Shivam Patel\Downloads\Antigravity_V4_Chat_Export.md")
out_path = Path(r"F:\Fleet_Master_Archive\Bot_13_V4_ML_Driven_Strategy\v4_options_hedging_latest_learnings.md")

print(f"Reading: {export_path}")
if not export_path.exists():
    print("Export file not found.")
else:
    with open(export_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    lines = content.split('\n')
    print(f"Total lines: {len(lines)}")
    
    # We will search for key headings and copy their text blocks
    # Headings and their approximate line ranges:
    # 1. Title & Key Metrics (1 to 650)
    # 2. V5 sweep (3360 to 3450)
    # 3. Bug and audit (4580 to 4820, 7280 to 7370, 7560 to 7600)
    # 4. V4 Performance (9570 to 9940)
    # 5. Live deploy & Scheduler (10200 to 10768)
    
    # Let's extract the key sections and construct a beautiful, detailed document
    sections = []
    
    # Section 1: Overview and Top Champions
    sections.append("## 1. Overview & Key Metrics Summary (Historical)")
    sections.append('\n'.join(lines[0:660]))
    
    # Section 2: V5 100K Parameter Sweep & V6 Bug
    sections.append("## 2. V5 Mega-Sweep & V6 Bug Analysis")
    sections.append('\n'.join(lines[3350:3500]))
    
    # Section 3: The Fatal Bug discovery & Code Fixes
    sections.append("## 3. The Forensic Audit, Bug Exterminations, and Lookahead Fixes")
    sections.append('\n'.join(lines[4590:4820]))
    sections.append("\n### Technical Code Fix Details\n")
    sections.append('\n'.join(lines[7280:7370]))
    sections.append('\n'.join(lines[7560:7600]))
    
    # Section 4: V4 ML Architecture and True Audited Performance
    sections.append("## 4. V4 ML-Driven Options Hedging Architecture & Audited Performance")
    sections.append('\n'.join(lines[9040:9300]))
    sections.append('\n'.join(lines[9570:9940]))
    
    # Section 5: Live Fleet Integration, Windows Task Scheduler & DeepSeek Auto-Medic
    sections.append("## 5. Live Production Deployment, Task Scheduler & DeepSeek Auto-Medic")
    sections.append('\n'.join(lines[10200:10768]))
    
    full_report = "\n\n".join(sections)
    
    # Write as UTF-8
    with open(out_path, "w", encoding="utf-8") as out_f:
        out_f.write(full_report)
        
    print(f"Successfully generated: {out_path.name}")
    print(f"Total report size: {len(full_report)} chars")
