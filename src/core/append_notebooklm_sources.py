
import json
import os
import glob

# 1. Read conversation transcript to get the raw user prompts
transcript_path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\35732b90-976f-4cc4-b3fe-7fc24c167fe0\.system_generated\logs\transcript.jsonl"
user_prompts = []
try:
    with open(transcript_path, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line.strip())
            if data.get('type') == 'USER_INPUT' and data.get('content'):
                user_prompts.append(data['content'])
except Exception as e:
    print(f"Error reading transcript: {e}")

# 2. Read astro_core.py
astro_core_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\astro_core.py"
astro_core_content = ""
try:
    with open(astro_core_path, 'r', encoding='utf-8') as f:
        astro_core_content = f.read()
except Exception as e:
    print(f"Error reading astro_core.py: {e}")

# 3. Read the existing NotebookLM Master
master_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\NotebookLM_Master_Knowledge_Base.md"
master_content = ""
try:
    with open(master_path, 'r', encoding='utf-8') as f:
        master_content = f.read()
except Exception as e:
    print(f"Error reading master file: {e}")

# 4. Append the new critical sections
with open(master_path, 'a', encoding='utf-8') as f:
    f.write("\n\n================================================================================\n")
    f.write("# THE RAW CONVERSATION HISTORY (USER'S VOICE AND INTENT)\n\n")
    f.write("This section captures the exact raw prompts provided by the User, establishing the driving philosophy, strict standards, and creative direction of the project.\n\n")
    for i, prompt in enumerate(user_prompts):
        f.write(f"### Prompt {i+1}\n```text\n{prompt.strip()}\n```\n\n")

    f.write("\n\n================================================================================\n")
    f.write("# THE PYTHON ENGINE CORE (`astro_core.py`)\n\n")
    f.write("This is the foundational Python code that handles the mathematical interaction with Swiss Ephemeris. It contains the Topocentric coordinates, Tropical aspect extraction, and Node schism solutions.\n\n")
    f.write(f"```python\n{astro_core_content}\n```\n\n")

print("Successfully injected raw user prompts and astro_core.py into the NotebookLM Master Knowledge Base.")
