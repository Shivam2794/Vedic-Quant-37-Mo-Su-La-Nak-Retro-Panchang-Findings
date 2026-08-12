import json
import sys

filepath = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\7b03663a-d01b-4302-8959-0a511c484299\.system_generated\logs\transcript_full.jsonl"
outpath = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\video3_description.txt"

with open(filepath, "r", encoding="utf-8") as f, open(outpath, "w", encoding="utf-8") as out:
    for line in f:
        data = json.loads(line)
        if data.get("type") == "USER_INPUT":
            content = data.get("content", "")
            if "below is the description of Video 3" in content:
                out.write(content)
                break
