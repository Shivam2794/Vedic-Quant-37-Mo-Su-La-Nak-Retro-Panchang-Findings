import json

def scan_transcript(file_path):
    print(f"Scanning {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if not line.strip(): continue
                try:
                    d = json.loads(line)
                    content = str(d.get('content', '')) + str(d.get('tool_calls', ''))
                    
                    if '.mp4' in content.lower() or 'bootcamp' in content.lower() or '25' in content.lower():
                        if 'download' in content.lower() or 'video' in content.lower():
                            if d.get('type') == 'USER_INPUT':
                                print(f"USER INPUT: {content}")
                            elif '.mp4' in content.lower():
                                print(f"MP4 Found Step {d.get('step_index')}: {content[:150]}...")
                except Exception as e:
                    pass
    except Exception as e:
        print(f"Error opening {file_path}: {e}")

scan_transcript(r'C:\Users\Shivam Patel\.gemini\antigravity\brain\40000e82-82bc-4b20-b8d0-8e8de4c18f23\.system_generated\logs\transcript.jsonl')
scan_transcript(r'C:\Users\Shivam Patel\.gemini\antigravity\brain\a252d513-5132-4d80-a20e-e71d4a2ea238\.system_generated\logs\transcript.jsonl')
