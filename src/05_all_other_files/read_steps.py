import json

def read_lines():
    path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\f7cdee3c-586a-4806-b281-db74f64d657a\.system_generated\logs\transcript.jsonl"
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    idx = data.get('step_index', 0)
                    if 55883 <= idx <= 55890:
                        print(f"STEP {idx} [{data.get('type')}]: {str(data)[:500]}")
                except Exception:
                    pass
    except Exception as e:
        print(e)

if __name__ == "__main__":
    read_lines()
