import json

def search_transcript():
    path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\f7cdee3c-586a-4806-b281-db74f64d657a\.system_generated\logs\transcript.jsonl"
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    content = data.get('content', '')
                    if content and ('github' in content.lower() or 'clone' in content.lower() or 'git ' in content.lower()):
                        print(f"[{data.get('type')}] {content[:500]}...\n")
                    
                    # Also check tool calls for commands run
                    if data.get('tool_calls'):
                        for tc in data['tool_calls']:
                            if tc['name'] == 'default_api:run_command':
                                cmd = tc['arguments'].get('CommandLine', '')
                                cwd = tc['arguments'].get('Cwd', '')
                                if 'git' in cmd.lower() or 'github' in cwd.lower():
                                    print(f"[TOOL_CALL run_command] {cwd} > {cmd}")
                except Exception:
                    pass
    except Exception as e:
        print(e)

if __name__ == "__main__":
    search_transcript()
