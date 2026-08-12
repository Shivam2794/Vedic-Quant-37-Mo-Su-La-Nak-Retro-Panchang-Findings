import json
import os
import glob
import re

search_terms = ["advanced momentum", "bot 2"]

output_dir = r"F:\Fleet_Master_Archive\Bot_2_Advanced_Momentum"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(os.path.join(output_dir, "code"), exist_ok=True)

brain_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\brain"
transcript_files = glob.glob(os.path.join(brain_dir, "*", ".system_generated", "logs", "transcript.jsonl"))

found_messages = []

for file in transcript_files:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    # check if it's a message containing search terms
                    # different formats of transcript logs could exist
                    content = str(data)
                    if any(term in content.lower() for term in search_terms):
                        found_messages.append({"file": file, "content": data})
                except:
                    pass
    except Exception as e:
        print(f"Error reading {file}: {e}")

with open(os.path.join(output_dir, "transcripts_raw.json"), 'w', encoding='utf-8') as out:
    json.dump(found_messages, out, indent=2)

print(f"Found {len(found_messages)} messages containing the search terms.")
