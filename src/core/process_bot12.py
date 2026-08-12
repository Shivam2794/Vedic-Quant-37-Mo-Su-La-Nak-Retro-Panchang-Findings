import json
import os
import re

msgs_file = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\bot12_msgs.json"
out_dir = r"F:\Fleet_Master_Archive\Bot_12_Deep_Advance_Autoresearch_Astro"
os.makedirs(os.path.join(out_dir, "code"), exist_ok=True)

with open(msgs_file, "r", encoding="utf-8") as f:
    msgs = json.load(f)

history = []
failures = []
backtests = []
codes = []

for msg in msgs:
    content = str(msg)
    
    # Try to find code blocks
    code_blocks = re.findall(r'```python(.*?)```', content, re.DOTALL)
    for i, code in enumerate(code_blocks):
        codes.append(code.strip())
        
    if "fail" in content.lower() or "error" in content.lower() or "bug" in content.lower() or "fix" in content.lower():
        failures.append(content)
        
    if "backtest" in content.lower() or "cagr" in content.lower() or "sharpe" in content.lower() or "return" in content.lower() or "drawdown" in content.lower():
        backtests.append(content)
        
    history.append(content)

with open(os.path.join(out_dir, "history.md"), "w", encoding="utf-8") as f:
    f.write("# History of Bot 12: Deep Advance Autoresearch Astro\n\n")
    for i, h in enumerate(history):
        f.write(f"## Entry {i}\n")
        f.write(h + "\n\n")

with open(os.path.join(out_dir, "failures_and_fixes.md"), "w", encoding="utf-8") as f:
    f.write("# Failures and Fixes\n\n")
    for i, h in enumerate(failures):
        f.write(f"## Issue {i}\n")
        f.write(h + "\n\n")

with open(os.path.join(out_dir, "backtests.md"), "w", encoding="utf-8") as f:
    f.write("# Backtest Results\n\n")
    for i, h in enumerate(backtests):
        f.write(f"## Result {i}\n")
        f.write(h + "\n\n")
        
for i, code in enumerate(codes):
    with open(os.path.join(out_dir, "code", f"snippet_{i}.py"), "w", encoding="utf-8") as f:
        f.write(code)
        
print("Processed", len(msgs), "messages.")
print("Extracted", len(codes), "code snippets.")
