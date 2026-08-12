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
    print(f"\n=======================================================")
    print(f"LATEST THINKING: {name} ({cid})")
    print(f"=======================================================")
    if not log_path.exists():
        print("No log file found.")
        continue
        
    last_thinking = None
    last_step = None
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                step = json.loads(line)
                if step.get("thinking"):
                    last_thinking = step.get("thinking")
                    last_step = step.get("step_index")
            except:
                pass
                
    if last_thinking:
        print(f"Step {last_step}:")
        safe_thinking = last_thinking.encode('ascii', 'replace').decode('ascii')
        print(safe_thinking[:2000] + ("\n... [TRUNCATED] ..." if len(last_thinking) > 2000 else ""))
    else:
        print("No thinking found yet.")
