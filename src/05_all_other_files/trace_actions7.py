import json

def trace_commands():
    path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\f7cdee3c-586a-4806-b281-db74f64d657a\.system_generated\logs\transcript.jsonl"
    
    found_step = False
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    
                    if not found_step:
                        if data.get('step_index', 0) >= 55883:
                            found_step = True
                    
                    if found_step:
                        if 'tool_calls' in data:
                            for tc in data['tool_calls']:
                                name = tc.get('name')
                                args = tc.get('arguments', {})
                                if name == 'default_api:run_command':
                                    print(args.get('CommandLine', ''))
                except Exception:
                    pass
    except Exception as e:
        print(e)

if __name__ == "__main__":
    trace_commands()
