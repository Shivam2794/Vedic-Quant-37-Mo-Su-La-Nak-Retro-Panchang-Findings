import json
import os

transcript_path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\40000e82-82bc-4b20-b8d0-8e8de4c18f23\.system_generated\logs\transcript.jsonl"
out_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\user_prompts.txt"

with open(transcript_path, 'r', encoding='utf-8') as f_in, open(out_path, 'w', encoding='utf-8') as f_out:
    for i, line in enumerate(f_in):
        try:
            data = json.loads(line)
            if data.get("type") == "USER_INPUT":
                content = data.get("content", "")
                f_out.write(f"STEP {i}:\n{content}\n" + "="*50 + "\n")
        except:
            pass
