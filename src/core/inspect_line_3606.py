import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

project_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\ml_options_hedging_project"
chat_history_path = os.path.join(project_dir, "docs", "chat_history.md")

with open(chat_history_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

print("".join(lines[3590:3620]))
