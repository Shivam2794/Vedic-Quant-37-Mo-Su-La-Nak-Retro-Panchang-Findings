import json

log_path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\ff521a99-56df-4cda-af2a-98ca5d5a4471\.system_generated\logs\transcript.jsonl"

print("Extracting model actions from 16:30 to 17:00...")
try:
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("source") == "MODEL" and entry.get("type") == "PLANNER_RESPONSE":
                    timestamp = entry.get("created_at")
                    if timestamp and "2026-07-21T16:30" <= timestamp <= "2026-07-21T17:30":
                        content = entry.get("content", "")
                        thinking = entry.get("thinking", "")
                        calls = entry.get("tool_calls", [])
                        if calls:
                            print(f"[{timestamp}] MODEL TOOL CALLS: {[c['name'] for c in calls]}")
                            for c in calls:
                                if c['name'] in ['write_to_file', 'replace_file_content', 'multi_replace_file_content']:
                                    print(f"  {c['name']}: {c['args'].get('TargetFile')}")
                        if content:
                            print(f"[{timestamp}] MODEL CONTENT:\n{content[:200]}...")
            except json.JSONDecodeError:
                pass
except Exception as e:
    print(f"Error: {e}")
