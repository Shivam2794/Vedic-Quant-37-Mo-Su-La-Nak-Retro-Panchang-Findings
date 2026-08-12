import os
import json

TARGET_DIR = r"F:\Fleet_Master_Archive\Bot_1_Hybrid_8_Sleeve"
mentions_file = os.path.join(TARGET_DIR, "hybrid_mentions.txt")

history_md = os.path.join(TARGET_DIR, "history.md")
failures_md = os.path.join(TARGET_DIR, "failures_and_fixes.md")
backtests_md = os.path.join(TARGET_DIR, "backtests.md")
readme = os.path.join(TARGET_DIR, "CLAUDE_HANDOFF_README.md")

with open(history_md, "w", encoding="utf-8") as f_hist, \
     open(failures_md, "w", encoding="utf-8") as f_fail, \
     open(backtests_md, "w", encoding="utf-8") as f_back:

    f_hist.write("# Bot 1 (Hybrid 8-Sleeve) - Complete History\n\n")
    f_fail.write("# Bot 1 (Hybrid 8-Sleeve) - Failures and Fixes\n\n")
    f_back.write("# Bot 1 (Hybrid 8-Sleeve) - Backtests\n\n")

    if os.path.exists(mentions_file):
        with open(mentions_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if "{" in line:
                    try:
                        # Extract the JSON part
                        json_str = line[line.find("{"):]
                        data = json.loads(json_str)
                        content = data.get("Content", "") or data.get("content", "") or data.get("Message", "")
                        timestamp = data.get("created_at", "") or data.get("Timestamp", "")
                        source = data.get("source", "")
                        
                        entry = f"## [{timestamp}] Source: {source}\n\n```text\n{content}\n```\n\n---\n\n"
                        
                        c_lower = content.lower()
                        # Always write to history to make it massive
                        f_hist.write(entry)
                        
                        if any(x in c_lower for x in ["error", "fail", "bug", "fix", "lesson", "false positive", "leakage"]):
                            f_fail.write(entry)
                            
                        if any(x in c_lower for x in ["backtest", "monte carlo", "cagr", "sharpe", "drawdown", "performance", "metric", "alpha"]):
                            f_back.write(entry)
                    except:
                        f_hist.write(f"## RAW LOG\n\n```text\n{line}\n```\n\n---\n\n")
                        f_fail.write(f"## RAW LOG\n\n```text\n{line}\n```\n\n---\n\n")
                        f_back.write(f"## RAW LOG\n\n```text\n{line}\n```\n\n---\n\n")
    else:
        f_hist.write("No mentions file found.\n")

with open(readme, "w", encoding="utf-8") as f:
    f.write("# CLAUDE HANDOFF - Bot 1: Hybrid 8-Sleeve\n\n")
    f.write("This archive contains a relentless, massive dump of all data, backtests, failures, and code for Bot 1 (Hybrid 8-Sleeve).\n\n")
    f.write("Files included:\n")
    f.write("- `code/`: Contains Python scripts (e.g., `check_fleet_status.py`, `fleet_watchdog.py`, `hybrid` module scripts).\n")
    f.write("- `history.md`: Complete raw conversational logs, analysis, and strategy building.\n")
    f.write("- `failures_and_fixes.md`: Extensive raw logs on bugs, data leakage, over-fitting catches, and lessons learned.\n")
    f.write("- `backtests.md`: Raw backtest performance metrics, Monte Carlo simulations, and OOS results.\n")

print("Done generating markdown files.")
