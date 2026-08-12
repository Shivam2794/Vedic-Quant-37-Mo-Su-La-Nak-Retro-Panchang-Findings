import json
import sys

filepath = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\7b03663a-d01b-4302-8959-0a511c484299\.system_generated\logs\transcript_full.jsonl"

with open(filepath, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        if data.get("type") == "USER_INPUT":
            print("="*40)
            # Only print first 500 chars of content for readability
            content = data.get("content", "")
            print(content[:1500])
