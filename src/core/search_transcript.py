import json
import re

log_path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\ff521a99-56df-4cda-af2a-98ca5d5a4471\.system_generated\logs\transcript.jsonl"

print("Searching transcript for user messages about bots...")
try:
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("type") == "USER_INPUT":
                    content = entry.get("content", "").lower()
                    if "holy grail" in content or "create" in content or "bot" in content:
                        print(f"[{entry.get('created_at')}] USER: {content[:200]}...")
            except json.JSONDecodeError:
                pass
except Exception as e:
    print(f"Error: {e}")
