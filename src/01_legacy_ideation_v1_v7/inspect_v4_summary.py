import re
from pathlib import Path

path = Path(r"C:\Users\Shivam Patel\.gemini\antigravity\brain\879cc675-1bac-47f1-9b56-8c074e27bd91\v4_options_hedging_latest_learnings.md")
if not path.exists():
    print("File not found.")
else:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    print(f"Total report size: {len(content)} characters")
    
    # Search for specific metrics or code blocks using regex
    # 1. Look for V5 Top 10 Champions or Champion Config
    v5_match = re.search(r"Top 10 Champions \(V5\).*?(?=##)", content, re.DOTALL | re.IGNORECASE)
    if v5_match:
        print("\n=== V5 SWEEP RESULTS ===")
        print(v5_match.group(0)[:1500].encode('ascii', 'replace').decode('ascii'))
        
    # 2. Look for the V6 Bug or VIX Mismatch
    bug_match = re.search(r"Bug: VIX Threshold Scaling Mismatch.*?(?=##)", content, re.DOTALL | re.IGNORECASE)
    if bug_match:
        print("\n=== VIX MISMATCH BUG ===")
        print(bug_match.group(0)[:1000].encode('ascii', 'replace').decode('ascii'))
        
    # 3. Look for the V4 Performance or THE TRUE V4 PERFORMANCE
    v4_match = re.search(r"THE TRUE V4 PERFORMANCE.*?(?=##)", content, re.DOTALL | re.IGNORECASE)
    if v4_match:
        print("\n=== TRUE V4 PERFORMANCE ===")
        print(v4_match.group(0)[:1500].encode('ascii', 'replace').decode('ascii'))
        
    # Let's search for "V4 Final Performance" or "Top 5"
    top5_match = re.search(r"Top 5 Overall Champions.*?(?=##)", content, re.DOTALL | re.IGNORECASE)
    if top5_match:
        print("\n=== TOP 5 CHAMPIONS ===")
        print(top5_match.group(0)[:1500].encode('ascii', 'replace').decode('ascii'))
