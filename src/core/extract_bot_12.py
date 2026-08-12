import json
import os
import re

transcripts = [
    r"C:\Users\Shivam Patel\.gemini\antigravity\brain\043965a0-6dff-4c4e-8271-1c3355194f5a\.system_generated\logs\transcript.jsonl",
    r"C:\Users\Shivam Patel\.gemini\antigravity\brain\072cbd5d-8854-4d8b-a6b7-f946f61edb9c\.system_generated\logs\transcript.jsonl",
    r"C:\Users\Shivam Patel\.gemini\antigravity\brain\0d364141-f489-42cb-98dd-bac569db7eb3\.system_generated\logs\transcript.jsonl",
    r"C:\Users\Shivam Patel\.gemini\antigravity\brain\35732b90-976f-4cc4-b3fe-7fc24c167fe0\.system_generated\logs\transcript.jsonl",
    r"C:\Users\Shivam Patel\.gemini\antigravity\brain\3d6dc5a2-311c-4ce1-8c1a-8a700a28a73f\.system_generated\logs\transcript.jsonl",
    r"C:\Users\Shivam Patel\.gemini\antigravity\brain\3ee4626e-1cf1-4f8c-a7c0-9fce411f3c7b\.system_generated\logs\transcript.jsonl",
    r"C:\Users\Shivam Patel\.gemini\antigravity\brain\41dcac32-3d80-4204-ac31-80f0ba0dfcb2\.system_generated\logs\transcript.jsonl",
    r"C:\Users\Shivam Patel\.gemini\antigravity\brain\41e6d2c9-da87-4446-8407-c67a4ecdc03c\.system_generated\logs\transcript.jsonl",
    r"C:\Users\Shivam Patel\.gemini\antigravity\brain\53af6ebd-55f2-4cf3-87db-7d18883a4eea\.system_generated\logs\transcript.jsonl",
    r"C:\Users\Shivam Patel\.gemini\antigravity\brain\65394f59-7ab7-4ae3-96bf-28e5714a2460\.system_generated\logs\transcript.jsonl",
    r"C:\Users\Shivam Patel\.gemini\antigravity\brain\6b0e063f-522d-4bc6-aa50-c9b33cf448d5\.system_generated\logs\transcript.jsonl",
    r"C:\Users\Shivam Patel\.gemini\antigravity\brain\8110fd12-9683-49eb-aefb-5aa1e6e3ac5c\.system_generated\logs\transcript.jsonl",
    r"C:\Users\Shivam Patel\.gemini\antigravity\brain\997e5227-2567-4664-b406-a6a05df92f52\.system_generated\logs\transcript.jsonl",
    r"C:\Users\Shivam Patel\.gemini\antigravity\brain\ac09686f-b2e2-4349-aa40-8ff7fa4bba80\.system_generated\logs\transcript.jsonl",
    r"C:\Users\Shivam Patel\.gemini\antigravity\brain\da93061d-9f92-40a2-b7f8-1ed211156c06\.system_generated\logs\transcript.jsonl",
    r"C:\Users\Shivam Patel\.gemini\antigravity\brain\f1287f1f-720e-42f9-bdfc-70bbc4adf856\.system_generated\logs\transcript.jsonl",
    r"C:\Users\Shivam Patel\.gemini\antigravity\brain\f5b4511a-f302-4a6a-bf2b-9a9b1e4e1bf8\.system_generated\logs\transcript.jsonl"
]

out_dir = r"F:\Fleet_Master_Archive\Bot_12_Deep_Advance_Autoresearch_Astro"
os.makedirs(os.path.join(out_dir, "code"), exist_ok=True)

msgs = []
for file_path in transcripts:
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    content = str(data)
                    if "Deep Advance" in content or "Bot 12" in content or "Autoresearch Astro" in content:
                        msgs.append(data)
                except Exception as e:
                    pass

with open(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\bot12_msgs.json", "w", encoding="utf-8") as f:
    json.dump(msgs, f, indent=4)
print("Extracted", len(msgs), "messages related to Bot 12.")
