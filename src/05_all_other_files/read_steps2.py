import json

def read_steps():
    path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\86ed51bb-ac58-46b1-95bc-0a79189d9c6d\.system_generated\logs\transcript.jsonl"
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    idx = data.get('step_index', 0)
                    if 503 <= idx <= 510:
                        if data.get('type') == 'PLANNER_RESPONSE':
                            print(f"STEP {idx} [PLANNER_RESPONSE]: {data.get('tool_calls')}")
                        elif data.get('type') == 'RUN_COMMAND':
                            print(f"STEP {idx} [RUN_COMMAND]: {data.get('content')}")
                        elif data.get('type') == 'CODE_ACTION':
                            print(f"STEP {idx} [CODE_ACTION]: {str(data.get('tool_calls', ''))[:200]}")
                except Exception:
                    pass
    except Exception as e:
        print(e)

if __name__ == "__main__":
    read_steps()
