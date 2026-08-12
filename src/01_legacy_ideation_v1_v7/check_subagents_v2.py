import json
import os
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
    print(f"\n=== {name} ({cid}) ===")
    
    # 1. Check artifacts directory
    art_dir = base_dir / cid / "artifacts"
    if art_dir.exists():
        files = os.listdir(art_dir)
        if files:
            print(f"Artifacts created: {files}")
            for f in files:
                if f.endswith('.md') and not f.endswith('.json'):
                    p = art_dir / f
                    print(f"  - Size of {f}: {p.stat().st_size} bytes")
        else:
            print("Artifacts directory exists but is empty.")
    else:
        print("No artifacts directory found yet.")
        
    # 2. Check last transcript log entries
    log_path = base_dir / cid / ".system_generated" / "logs" / "transcript.jsonl"
    if log_path.exists():
        last_lines = []
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                last_lines.append(line)
        
        print(f"Transcript lines: {len(last_lines)}")
        # Look at the last few lines to see what's happening
        for idx in range(max(0, len(last_lines)-4), len(last_lines)):
            try:
                step = json.loads(last_lines[idx])
                source = step.get("source")
                stype = step.get("type")
                status = step.get("status")
                print(f"  Step {step.get('step_index')}: {source} -> {stype} ({status})")
                if source == "MODEL":
                    content = step.get("content")
                    if content and len(content.strip()) > 0:
                        print(f"    Content (first 100 chars): {content[:100].strip()}...")
                    thinking = step.get("thinking")
                    if thinking and len(thinking.strip()) > 0:
                        print(f"    Thinking (first 100 chars): {thinking[:100].strip()}...")
            except Exception as e:
                pass
    else:
        print("No transcript log found.")
