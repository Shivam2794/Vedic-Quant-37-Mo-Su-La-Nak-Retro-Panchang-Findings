import os
import json
import re
from pathlib import Path

CHAT_IDS = [
    "7b03663a-d01b-4302-8959-0a511c484299", # Root
    "083b0f8a-28ff-4962-bf24-e3339c053c6a", # Chat 1
    "0408ba04-b110-46c2-8c78-843f3a46a017", # Chat 2
    "a252d513-5132-4d80-a20e-e71d4a2ea238"  # Chat 3
]

BRAIN_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\brain"
SCRATCH_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"

def analyze_transcripts():
    all_files = set()
    user_prompts = []
    model_responses = []
    
    for cid in CHAT_IDS:
        transcript_path = os.path.join(BRAIN_DIR, cid, ".system_generated", "logs", "transcript_full.jsonl")
        if not os.path.exists(transcript_path):
            print(f"MISSING TRANSCRIPT: {transcript_path}")
            continue
            
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    step_type = entry.get('type')
                    content = entry.get('content', '')
                    
                    if step_type == 'USER_INPUT':
                        user_prompts.append((cid, content))
                        
                    elif step_type == 'PLANNER_RESPONSE':
                        model_responses.append((cid, content))
                        
                    if 'tool_calls' in entry:
                        for call in entry['tool_calls']:
                            if call['name'] in ['write_to_file', 'replace_file_content', 'multi_replace_file_content']:
                                args = call.get('arguments', {})
                                target = args.get('TargetFile') or args.get('AbsolutePath') or args.get('Target')
                                if target:
                                    all_files.add((cid, target))
                except Exception as e:
                    pass
                    
    return all_files, user_prompts, model_responses

def discover_physical_files():
    found_files = []
    
    # Check scratch dir
    for root, dirs, files in os.walk(SCRATCH_DIR):
        for file in files:
            p = os.path.join(root, file)
            # ignore __pycache__ and big parquet data files for code audit
            if '__pycache__' in p or p.endswith('.parquet') or p.endswith('.csv'):
                continue
            found_files.append(p)
            
    # Check brain artifacts for each chat
    for cid in CHAT_IDS:
        chat_dir = os.path.join(BRAIN_DIR, cid)
        if os.path.exists(chat_dir):
            for file in os.listdir(chat_dir):
                if file.endswith('.md') or file.endswith('.json') or file.endswith('.py'):
                    found_files.append(os.path.join(chat_dir, file))
                    
    return found_files

if __name__ == "__main__":
    all_files, user_prompts, model_responses = analyze_transcripts()
    physical_files = discover_physical_files()
    
    out = {
        "transcript_files_touched": list(all_files),
        "physical_files_found": physical_files,
        "total_user_prompts": len(user_prompts),
        "total_model_responses": len(model_responses)
    }
    
    with open('audit_summary.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=4)
    print("Audit extraction complete.")
