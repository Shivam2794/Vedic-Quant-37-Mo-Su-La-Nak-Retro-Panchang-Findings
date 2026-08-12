import json
import os
import re

CHAT_IDS = {
    "7b03663a-d01b-4302-8959-0a511c484299": "Root Project",
    "083b0f8a-28ff-4962-bf24-e3339c053c6a": "Chat 1",
    "0408ba04-b110-46c2-8c78-843f3a46a017": "Chat 2",
    "a252d513-5132-4d80-a20e-e71d4a2ea238": "Chat 3 (Main Continuation)"
}
BRAIN_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\brain"

keywords = re.compile(r'\b(must|never|always|constraint|architecture|bootcamp|mandate|forbidden|rule|limit|limitations|edge case|bug|failed|error|strict)\b', re.IGNORECASE)

def extract():
    results = []
    
    for cid, label in CHAT_IDS.items():
        transcript_path = os.path.join(BRAIN_DIR, cid, ".system_generated", "logs", "transcript_full.jsonl")
        if not os.path.exists(transcript_path):
            continue
            
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    # We primarily care about user prompts for constraints, but also model plans
                    if entry.get('type') in ['USER_INPUT', 'PLANNER_RESPONSE']:
                        content = entry.get('content', '')
                        if keywords.search(content):
                            # extract surrounding context
                            sentences = content.split('\n')
                            for s in sentences:
                                if keywords.search(s) and len(s.strip()) > 10:
                                    results.append(f"[{label}] {s.strip()}")
                except Exception:
                    pass
                    
    # Deduplicate and sort
    results = sorted(list(set(results)))
    
    with open('extracted_raw_constraints.txt', 'w', encoding='utf-8') as f:
        for r in results:
            f.write(r + "\n")
            
    print(f"Extracted {len(results)} constraint candidates.")

if __name__ == '__main__':
    extract()
