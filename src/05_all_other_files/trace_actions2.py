import json

def trace_actions():
    paths = [
        r"C:\Users\Shivam Patel\.gemini\antigravity\brain\f7cdee3c-586a-4806-b281-db74f64d657a\.system_generated\logs\transcript.jsonl",
        r"C:\Users\Shivam Patel\.gemini\antigravity\brain\86ed51bb-ac58-46b1-95bc-0a79189d9c6d\.system_generated\logs\transcript.jsonl"
    ]
    
    found_ledger = False
    
    for path in paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        content = data.get('content', '')
                        
                        if 'type' in data and data['type'] == 'USER_INPUT':
                            if 'FLAWS_AND_FIXES_LEDGER.md' in content and not found_ledger:
                                print(f"\n--- FOUND INITIAL DIRECTIVE ---")
                                found_ledger = True
                        
                        if found_ledger and 'tool_calls' in data:
                            for tc in data['tool_calls']:
                                name = tc.get('name')
                                args = tc.get('arguments', {})
                                if name == 'default_api:run_command':
                                    cmd = args.get('CommandLine', '')
                                    print(f"RUN: {cmd}")
                                elif name == 'default_api:write_to_file':
                                    tf = args.get('TargetFile', '')
                                    print(f"WRITE: {tf}")
                                elif name == 'default_api:view_file':
                                    tf = args.get('AbsolutePath', '')
                                    print(f"VIEW: {tf}")
                                elif name == 'default_api:multi_replace_file_content':
                                    tf = args.get('TargetFile', '')
                                    print(f"MULTI_REPLACE: {tf}")
                                elif name == 'default_api:replace_file_content':
                                    tf = args.get('TargetFile', '')
                                    print(f"REPLACE: {tf}")
                    except Exception:
                        pass
        except Exception as e:
            print(f"Error opening {path}: {e}")

if __name__ == "__main__":
    trace_actions()
