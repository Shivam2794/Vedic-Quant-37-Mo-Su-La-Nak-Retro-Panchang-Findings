import os
from pathlib import Path

downloads = Path(r"C:\Users\Shivam Patel\Downloads")
exports = ["Antigravity_V4_Chat_Export.md", "Antigravity_Chat_Export.md"]

for name in exports:
    p = downloads / name
    print(f"\n=======================================================")
    print(f"SEARCHING: {name}")
    print(f"=======================================================")
    if not p.exists():
        print("File does not exist.")
        continue
        
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()
        
    print(f"File Size: {len(content)} chars")
    
    # Check if specific terms are present
    terms = ["regime_quant_ml", "mega_epoch", "T+1", "lookahead", "Bajo", "scraped_quant_ideas", "scraped_strategy_foundation"]
    for t in terms:
        count = content.lower().count(t.lower())
        print(f"  Term '{t}': {count} occurrences")
        
    # Find some headings
    lines = content.split('\n')
    headings = [l for l in lines if l.startswith('#')][:25]
    print("Headings:")
    for h in headings:
        safe_h = h.encode('ascii', 'replace').decode('ascii')
        print(f"  {safe_h}")
