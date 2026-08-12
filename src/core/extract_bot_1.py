import os
import json
import shutil
import re

BRAIN_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\brain"
SCRATCH_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
TARGET_DIR = r"F:\Fleet_Master_Archive\Bot_1_Hybrid_8_Sleeve"
CODE_DIR = os.path.join(TARGET_DIR, "code")

os.makedirs(CODE_DIR, exist_ok=True)

keywords = ["hybrid 8-sleeve", "bot 1", "hybrid", "8-sleeve", "bot_1", "bot1", "epoch21", "genesis"]

# 1. Extract Chat Logs
history_md = os.path.join(TARGET_DIR, "history.md")
failures_md = os.path.join(TARGET_DIR, "failures_and_fixes.md")
backtests_md = os.path.join(TARGET_DIR, "backtests.md")

hist_f = open(history_md, "w", encoding="utf-8")
fail_f = open(failures_md, "w", encoding="utf-8")
back_f = open(backtests_md, "w", encoding="utf-8")

hist_f.write("# Bot 1 (Hybrid 8-Sleeve) - Complete History\n\n")
fail_f.write("# Bot 1 (Hybrid 8-Sleeve) - Failures and Fixes\n\n")
back_f.write("# Bot 1 (Hybrid 8-Sleeve) - Backtests\n\n")

print("Extracting chat logs...")
for root, dirs, files in os.walk(BRAIN_DIR):
    for f in files:
        if f.endswith(".jsonl"):
            path = os.path.join(root, f)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as file:
                    for line in file:
                        line_lower = line.lower()
                        if any(k in line_lower for k in keywords):
                            try:
                                data = json.loads(line)
                                content = data.get("Content", "")
                                if not content and "Message" in data:
                                    content = data["Message"]
                            except:
                                content = line # Fallback to raw line
                                
                            if len(content) > 10:
                                entry = f"## Entry\n\n{content}\n\n---\n\n"
                                
                                c_lower = content.lower()
                                if any(x in c_lower for x in ["error", "fail", "bug", "fix", "lesson"]):
                                    fail_f.write(entry)
                                elif any(x in c_lower for x in ["backtest", "monte carlo", "cagr", "sharpe", "drawdown", "performance", "metric"]):
                                    back_f.write(entry)
                                
                                hist_f.write(entry)
                                # To guarantee MASSIVE size, we'll write the context as well
                                for _ in range(5):  # Duplicate a bit if it's too small? No, user wants RAW logs. We'll just write it.
                                    pass
            except Exception as e:
                pass

hist_f.close()
fail_f.close()
back_f.close()

# 2. Extract Code Files
print("Extracting code...")
copied = 0
for root, dirs, files in os.walk(SCRATCH_DIR):
    if any(x in root for x in ["venv", "node_modules", ".git", "__pycache__", ".venv"]):
        continue
    for f in files:
        if f.endswith((".py", ".json", ".md", ".sql", ".ps1", ".log", ".txt")):
            path = os.path.join(root, f)
            try:
                # 1. By filename
                if any(kw in f.lower() for kw in keywords):
                    shutil.copy2(path, os.path.join(CODE_DIR, f))
                    copied += 1
                    continue
                
                # 2. By content
                with open(path, "r", encoding="utf-8", errors="ignore") as file:
                    content = file.read()
                    c_lower = content.lower()
                    if "hybrid 8-sleeve" in c_lower or "bot 1" in c_lower:
                        shutil.copy2(path, os.path.join(CODE_DIR, f))
                        copied += 1
            except Exception as e:
                pass

print(f"Copied {copied} files to {CODE_DIR}")
