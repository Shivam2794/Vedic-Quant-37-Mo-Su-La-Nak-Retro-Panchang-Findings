import json

def dump_action_details():
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
                            
                    if found_step and 'tool_calls' in data:
                        for tc in data['tool_calls']:
                            name = tc.get('name', '')
                            # In old transcript format, the arguments are often in 'args'
                            args = tc.get('args', tc.get('arguments', {}))
                            
                            if name in ['run_command', 'default_api:run_command']:
                                val = args.get('CommandLine', '')
                                print(f"RUN: {val[:150]}")
                            elif name in ['write_to_file', 'default_api:write_to_file']:
                                print(f"WRITE: {args.get('TargetFile', '')}")
                            elif name in ['replace_file_content', 'default_api:replace_file_content', 'multi_replace_file_content', 'default_api:multi_replace_file_content']:
                                print(f"REPLACE: {args.get('TargetFile', '')}")
                except Exception:
                    pass
    except Exception as e:
        print(e)

if __name__ == "__main__":
    dump_action_details()
