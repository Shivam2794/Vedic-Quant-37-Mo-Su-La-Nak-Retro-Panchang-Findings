import json

def get_user_inputs():
    path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\86ed51bb-ac58-46b1-95bc-0a79189d9c6d\.system_generated\logs\transcript.jsonl"
    count = 0
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                if data.get('type') == 'USER_INPUT':
                    print(f"[{count+1}] {data.get('content')}")
                    count += 1
            except Exception as e:
                pass

if __name__ == "__main__":
    get_user_inputs()
