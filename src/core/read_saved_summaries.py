import os
from pathlib import Path

base_dir = Path(r"C:\Users\Shivam Patel\.gemini\antigravity\brain\879cc675-1bac-47f1-9b56-8c074e27bd91")

summaries = [
    "scraper_strategy_chat_reader_summary.md",
    "genesis_optimization_reader_2_summary.md",
    "mega_epoch_detail_reader_summary.md"
]

for s in summaries:
    p = base_dir / s
    print(f"\n=======================================================")
    print(f"FILE: {s}")
    print(f"=======================================================")
    if not p.exists():
        print("File does not exist.")
        continue
    
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()
        
    print(f"Total Size: {len(content)} characters")
    
    # Extract headers (lines starting with #)
    lines = content.split('\n')
    headers = [l for l in lines if l.startswith('#')]
    print("Headers found:")
    for h in headers[:20]:
        print(f"  {h}")
        
    print("\n--- Summary Content Snippet ---")
    # Print the first 2000 chars safely
    safe_snippet = content[:3000].encode('ascii', 'replace').decode('ascii')
    print(safe_snippet + ("\n... [TRUNCATED] ..." if len(content) > 3000 else ""))
