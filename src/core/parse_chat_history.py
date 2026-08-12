import json

transcript_path = r'C:\Users\Shivam Patel\.gemini\antigravity\brain\879cc675-1bac-47f1-9b56-8c074e27bd91\.system_generated\logs\transcript.jsonl'
output_path = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\chat_summary.txt'

with open(transcript_path, 'r', encoding='utf-8') as f, open(output_path, 'w', encoding='utf-8') as out:
    for line in f:
        try:
            data = json.loads(line)
            step_type = data.get('type')
            source = data.get('source')
            if step_type == 'USER_INPUT':
                out.write(f'\n--- USER STEP {data.get("step_index")} ---\n')
                out.write(data.get('content', '') + '\n')
            elif step_type == 'PLANNER_RESPONSE' or source == 'MODEL':
                if data.get('content'):
                    out.write(f'\n--- MODEL TEXT {data.get("step_index")} ---\n')
                    content = data.get('content', '')
                    if len(content) > 500:
                        content = content[:500] + '... [TRUNCATED]'
                    out.write(content + '\n')
        except:
            pass
print('Done parsing transcript.')
