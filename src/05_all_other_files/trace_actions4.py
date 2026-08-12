import json

def trace_actions():
    path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\86ed51bb-ac58-46b1-95bc-0a79189d9c6d\.system_generated\logs\transcript.jsonl"
    
    found_ledger = False
    count = 0
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    content = data.get('content', '')
                    
                    if 'type' in data and data['type'] == 'USER_INPUT':
                        if 'FLAWS_AND_FIXES_LEDGER.md' in content and not found_ledger:
                            print(f"--- FOUND DIRECTIVE IN {path} ---")
                            found_ledger = True
                    
                    if found_ledger and 'tool_calls' in data:
                        for tc in data['tool_calls']:
                            name = tc.get('name')
                            args = tc.get('arguments', {})
                            if name == 'default_api:run_command':
                                count += 1
                                print(f"RUN: {args.get('CommandLine', '')[:50]}")
                            elif name == 'default_api:write_to_file':
                                count += 1
                                print(f"WRITE: {args.get('TargetFile', '')}")
                            elif name == 'default_api:view_file':
                                count += 1
                                print(f"VIEW: {args.get('AbsolutePath', '')}")
                except Exception:
                    pass
    except Exception as e:
        print(f"Error opening {path}: {e}")
        
    print(f"Total tools executed after directive: {count}")

if __name__ == "__main__":
    trace_actions()
