import json

def trace_created_files():
    path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\f7cdee3c-586a-4806-b281-db74f64d657a\.system_generated\logs\transcript.jsonl"
    
    files_created = set()
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
                                if name == 'default_api:write_to_file':
                                    files_created.add(args.get('TargetFile', ''))
                                elif name == 'default_api:multi_replace_file_content' or name == 'default_api:replace_file_content':
                                    files_created.add(args.get('TargetFile', ''))
                except Exception:
                    pass
    except Exception as e:
        print(e)
        
    for f in sorted(list(files_created)):
        print(f)

if __name__ == "__main__":
    trace_created_files()
