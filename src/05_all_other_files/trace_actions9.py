import json

def trace_all_commands():
    path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\f7cdee3c-586a-4806-b281-db74f64d657a\.system_generated\logs\transcript.jsonl"
    
    found_step = False
    commands_run = 0
    files_created = 0
    files_modified = 0
    
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
                            # Account for both raw tool names and default_api prefix
                            if name in ['run_command', 'default_api:run_command']:
                                commands_run += 1
                            elif name in ['write_to_file', 'default_api:write_to_file']:
                                files_created += 1
                            elif name in ['replace_file_content', 'default_api:replace_file_content', 'multi_replace_file_content', 'default_api:multi_replace_file_content']:
                                files_modified += 1
                except Exception:
                    pass
    except Exception as e:
        print(e)
        
    print(f"Commands run: {commands_run}")
    print(f"Files created: {files_created}")
    print(f"Files modified: {files_modified}")

if __name__ == "__main__":
    trace_all_commands()
