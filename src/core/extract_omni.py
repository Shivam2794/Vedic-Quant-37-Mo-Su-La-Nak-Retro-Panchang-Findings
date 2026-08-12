import json
import glob
import os

target_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\brain"
transcripts = glob.glob(os.path.join(target_dir, "*", ".system_generated", "logs", "transcript.jsonl"))

history = []
failures = []
backtests = []

for t_file in transcripts:
    with open(t_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                if data.get("source") in ["USER", "MODEL"] and "content" in data:
                    content = data["content"]
                    if "omni" in content.lower():
                        history.append(content)
                        if any(w in content.lower() for w in ["fail", "fix", "lesson", "bug"]):
                            failures.append(content)
                        if any(w in content.lower() for w in ["backtest", "monte carlo", "sharpe", "cagr", "drawdown"]):
                            backtests.append(content)
            except:
                pass

with open(r"F:\Fleet_Master_Archive\Bot_3_Omni_V2_Screener\history.md", "w", encoding="utf-8") as f:
    f.write("# Omni-V2 Screener History\n\n")
    for idx, item in enumerate(history):
        f.write(f"## Entry {idx+1}\n{item}\n\n")

with open(r"F:\Fleet_Master_Archive\Bot_3_Omni_V2_Screener\failures_and_fixes.md", "w", encoding="utf-8") as f:
    f.write("# Failures and Fixes\n\n")
    for idx, item in enumerate(failures):
        f.write(f"## Issue {idx+1}\n{item}\n\n")

with open(r"F:\Fleet_Master_Archive\Bot_3_Omni_V2_Screener\backtests.md", "w", encoding="utf-8") as f:
    f.write("# Backtesting and Performance\n\n")
    for idx, item in enumerate(backtests):
        f.write(f"## Backtest {idx+1}\n{item}\n\n")

print(f"Extracted {len(history)} history entries, {len(failures)} failures, {len(backtests)} backtests.")
