import json

log_path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\ff521a99-56df-4cda-af2a-98ca5d5a4471\.system_generated\logs\transcript.jsonl"

print("Extracting model actions from 18:15 to 18:35...")
try:
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("source") == "MODEL" and entry.get("type") == "PLANNER_RESPONSE":
                    timestamp = entry.get("created_at")
                    if timestamp and "2026-07-21T18:15" <= timestamp <= "2026-07-21T18:35":
                        calls = entry.get("tool_calls", [])
                        if calls:
                            print(f"[{timestamp}] MODEL TOOL CALLS:")
                            for c in calls:
                                if c['name'] in ['write_to_file', 'replace_file_content', 'multi_replace_file_content']:
                                    print(f"  {c['name']}: {c['args'].get('TargetFile')} -> {c['args'].get('toolSummary')}")
            except json.JSONDecodeError:
                pass
except Exception as e:
    print(f"Error: {e}")
