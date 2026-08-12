import os
import json
import glob
import textwrap

downloads_md = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\downloads_md.txt"
with open(downloads_md, "r", encoding="utf-16") as f:
    d_files = f.read().splitlines()

jsonl_files = glob.glob(r"C:\Users\Shivam Patel\.gemini\antigravity\brain\*\.system_generated\logs\transcript.jsonl")

all_files = d_files + jsonl_files

for path in all_files:
    if not path.strip(): continue
    try:
        if path.endswith(".jsonl"):
            text_blocks = []
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        d = json.loads(line)
                        if 'content' in d and d['content']:
                            text_blocks.append(d['content'])
                    except:
                        pass
            content = "\n".join(text_blocks)
        else:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        
        # Grab first 1000 characters to evaluate
        preview = textwrap.shorten(content, width=800, placeholder="...")
        print(f"--- FILE: {path} ---")
        print(preview)
        print("\n")
    except Exception as e:
        print(f"Error on {path}: {e}")
