import json

def trace_mentions():
    paths = [
        r"C:\Users\Shivam Patel\.gemini\antigravity\brain\f7cdee3c-586a-4806-b281-db74f64d657a\.system_generated\logs\transcript.jsonl",
        r"C:\Users\Shivam Patel\.gemini\antigravity\brain\86ed51bb-ac58-46b1-95bc-0a79189d9c6d\.system_generated\logs\transcript.jsonl"
    ]
    
    for path in paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for idx, line in enumerate(f):
                    try:
                        data = json.loads(line)
                        content = data.get('content', '')
                        
                        if 'type' in data and data['type'] == 'USER_INPUT':
                            if 'FLAWS_AND_FIXES_LEDGER.md' in content:
                                print(f"[{path.split('brain')[1]}] STEP {data.get('step_index')}:\n{content[:200]}...\n")
                    except Exception:
                        pass
        except Exception as e:
            print(f"Error opening {path}: {e}")

if __name__ == "__main__":
    trace_mentions()
