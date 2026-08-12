import json
import os
from pathlib import Path

in_path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\ac09686f-b2e2-4349-aa40-8ff7fa4bba80\.system_generated\logs\transcript.jsonl"
out_path = r"C:\Users\Shivam Patel\Downloads\USA vedic quant project 2.txt"

out_lines = ["# USA Vedic Quant Project 2 - Chat History\n"]

with open(in_path, 'r', encoding='utf-8') as f:
    for line in f:
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            step_type = data.get("type", "")
            source = data.get("source", "")
            content = data.get("content", "")
            
            if not content:
                continue
                
            # Clean up user request wrapper tags
            if step_type == "USER_INPUT":
                if "<USER_REQUEST>" in content:
                    content = content.split("<USER_REQUEST>")[1].split("</USER_REQUEST>")[0].strip()
                out_lines.append(f"\n## 👤 User\n{content}\n")
            elif source == "MODEL" and step_type in ("PLANNER_RESPONSE", "ASSISTANT_RESPONSE", "MODEL_RESPONSE"):
                out_lines.append(f"\n## 🤖 Assistant\n{content}\n")
        except Exception as e:
            pass

with open(out_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(out_lines))

print(f"Exported successfully to {out_path}")
