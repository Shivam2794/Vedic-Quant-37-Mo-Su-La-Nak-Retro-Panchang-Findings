import json
import re
from datetime import datetime

log_path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\ff521a99-56df-4cda-af2a-98ca5d5a4471\.system_generated\logs\transcript.jsonl"

print("Extracting user messages between 15:00 and 18:30...")
try:
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("type") == "USER_INPUT":
                    timestamp = entry.get("created_at")
                    if timestamp and "2026-07-21T16:" <= timestamp <= "2026-07-21T18:":
                        content = entry.get("content", "")
                        print(f"[{timestamp}] USER:\n{content}\n")
            except json.JSONDecodeError:
                pass
except Exception as e:
    print(f"Error: {e}")
