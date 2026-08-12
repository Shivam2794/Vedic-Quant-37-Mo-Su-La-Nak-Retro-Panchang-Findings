import json
import glob
import os
import re

logs = glob.glob(r"C:\Users\Shivam Patel\.gemini\antigravity\brain\*\.system_generated\logs\transcript.jsonl")

conversations = []
for log in logs:
    has_bot5 = False
    lines = []
    with open(log, 'r', encoding='utf-8') as f:
        for line in f:
            lines.append(line)
            if "Advance Auto Research Astro" in line or "Bot 5" in line:
                has_bot5 = True
    if has_bot5:
        conversations.append((log, lines))

print(f"Found {len(conversations)} conversations with Bot 5.")

# We will save the entire text of these conversations to history.md, backtests.md, failures.md
history_lines = []
backtests_lines = []
failures_lines = []
files_mentioned = set()

for log, lines in conversations:
    conv_id = log.split('\\')[-4]
    history_lines.append(f"\n\n# Conversation ID: {conv_id}\n")
    for line in lines:
        try:
            data = json.loads(line)
            if 'content' in data:
                content = data['content']
                if "Advance Auto Research Astro" in content or "Bot 5" in content or "astro" in content.lower():
                    history_lines.append(f"## Step {data.get('step_index')}\n{content}\n")
                    
                    if "backtest" in content.lower() or "cagr" in content.lower() or "sharpe" in content.lower():
                        backtests_lines.append(f"## Step {data.get('step_index')}\n{content}\n")
                    
                    if "fail" in content.lower() or "error" in content.lower() or "fix" in content.lower() or "lesson" in content.lower():
                        failures_lines.append(f"## Step {data.get('step_index')}\n{content}\n")

                # Look for python files
                matches = re.findall(r'([a-zA-Z0-9_]+\.py)', content)
                for match in matches:
                    files_mentioned.add(match)
        except:
            pass

# Write out the files to F:\Fleet_Master_Archive\Bot_5_Advance_Auto_Research_Astro
base_dir = r"F:\Fleet_Master_Archive\Bot_5_Advance_Auto_Research_Astro"
os.makedirs(base_dir, exist_ok=True)

with open(os.path.join(base_dir, "history.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(history_lines))

with open(os.path.join(base_dir, "backtests.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(backtests_lines))

with open(os.path.join(base_dir, "failures_and_fixes.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(failures_lines))

print(f"Files mentioned: {files_mentioned}")
