import json

def search_transcript():
    path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\f7cdee3c-586a-4806-b281-db74f64d657a\.system_generated\logs\transcript.jsonl"
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if data.get('type') == 'USER_INPUT':
                        content = data.get('content', '')
                        if 'github' in content.lower() or 'repo' in content.lower() or 'git ' in content.lower():
                            print(f"[USER] {content}\n")
                except Exception:
                    pass
    except Exception as e:
        print(e)

if __name__ == "__main__":
    search_transcript()
