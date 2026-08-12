import json
from pathlib import Path

base_dir = Path(r"C:\Users\Shivam Patel\.gemini\antigravity\brain")
own_cid = "879cc675-1bac-47f1-9b56-8c074e27bd91"
log_path = base_dir / own_cid / ".system_generated" / "logs" / "transcript.jsonl"

print(f"Reading own transcript: {log_path}")
if not log_path.exists():
    print("Transcript does not exist.")
else:
    steps_count = 0
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                step = json.loads(line)
                steps_count += 1
                # We want to see messages from other agents or subagents that we received
                # System or model inputs that might contain the messages
                stype = step.get("type")
                source = step.get("source")
                print(f"Step {step.get('step_index')}: {source} -> {stype}")
                
                # Check if it has content with sender info
                content = step.get("content")
                if content and "sender=" in content:
                    print(f"  Received message in content! Length: {len(content)}")
                    print(content[:500] + "...")
            except Exception as e:
                pass
    print(f"Total steps: {steps_count}")
