import os
import re

project_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\ml_options_hedging_project"
chat_history_path = os.path.join(project_dir, "docs", "chat_history.md")

if not os.path.exists(chat_history_path):
    print("chat_history.md does not exist.")
    exit(1)

with open(chat_history_path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

print(f"Loaded chat_history.md: {len(content)} bytes.")

# Search for the Python filenames we need:
targets = [
    "ssvi_calibrator.py",
    "intraday_interpolator.py",
    "microstructure_layer.py",
    "validation_suite.py",
    "anchor_generator.py",
    "gpu_historical_tick_generator.py",
    "run_massive_generation.py",
    "vix_anchor_generator.py",
    "run_massive_generation_parallel.py"
]

for t in targets:
    count = len(re.findall(t, content, re.IGNORECASE))
    print(f"  {t}: {count} occurrences")
