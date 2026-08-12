import json
from pathlib import Path

subagents = {
    "Scraper Strategy Chat Reader": "7579e711-0501-441f-8966-5e9da11a3d52",
    "Genesis Optimization Reader 1": "f77a6985-78c0-4184-b6b3-0e8a1127dc4a",
    "Genesis Optimization Reader 2": "a9410c1d-506f-4e2f-afea-bd0044430f0a",
    "Mega Epoch Detail Reader": "ef2d2a27-b26f-45c1-aefd-9a2aaef47229",
    "Failed Epochs & Hedging Reader": "74cd5418-9e94-4a7a-ab4d-a84d7c383f5d",
    "Vedic Research & V4 Reader": "f888180d-db14-4d7f-a0c9-6d2aba0e9519",
    "Scrapper Chat Transcript Reader": "3376ac18-8d90-456c-833f-3a74a23da649"
}

base_dir = Path(r"C:\Users\Shivam Patel\.gemini\antigravity\brain")

for name, cid in subagents.items():
    log_path = base_dir / cid / ".system_generated" / "logs" / "transcript.jsonl"
    print(f"\n=== {name} ({cid}) ===")
    if not log_path.exists():
        print("Transcript does not exist yet.")
        continue
    
    # Read the transcript and find the last model response or agent message
    last_response = None
    steps_count = 0
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                step = json.loads(line)
                steps_count += 1
                if step.get("source") == "MODEL" and step.get("type") in ["PLANNER_RESPONSE", "FINAL_RESPONSE"]:
                    # Check if there is text content
                    content = step.get("content")
                    if content and len(content.strip()) > 0:
                        last_response = content
            except Exception as e:
                pass
    
    print(f"Total steps in log: {steps_count}")
    if last_response:
        # Print first 200 chars and last 200 chars of the last response
        lines = last_response.split('\n')
        print(f"Content Length: {len(last_response)} characters, {len(lines)} lines")
        if len(last_response) > 1000:
            print(last_response[:500] + "\n... [TRUNCATED] ...\n" + last_response[-500:])
        else:
            print(last_response)
    else:
        print("No model response found in transcript yet.")
