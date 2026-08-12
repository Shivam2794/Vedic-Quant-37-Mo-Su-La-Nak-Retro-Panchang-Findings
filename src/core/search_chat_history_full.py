import os
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

project_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\ml_options_hedging_project"
chat_history_path = os.path.join(project_dir, "docs", "chat_history.md")

with open(chat_history_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

keywords = ["ssvi", "interpolator", "microstructure", "generator", "validation", "vix_anchor", "parallel"]

for kw in keywords:
    matches = []
    for i, line in enumerate(lines):
        if kw.lower() in line.lower():
            matches.append(i + 1)
    print(f"Keyword '{kw}': {len(matches)} matches. First 10 lines: {matches[:10]}")
