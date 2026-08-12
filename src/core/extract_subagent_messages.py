import json
import sys
from pathlib import Path

# Configure stdout to use utf-8 if possible
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

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
    print(f"SUBAGENT: {name} ({cid})")
    print(f"=======================================================")
    if not log_path.exists():
        print("No log file found.")
        continue
        
    messages_sent = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                step = json.loads(line)
                # Check for tool_calls that are send_message
                tool_calls = step.get("tool_calls", [])
                for tc in tool_calls:
                    if tc.get("name") == "send_message":
                        args = tc.get("args", {})
                        if isinstance(args, str):
                            try:
                                args = json.loads(args)
                            except:
                                pass
                        msg = args.get("Message")
                        if msg:
                            messages_sent.append((step.get("step_index"), msg))
            except Exception as e:
                pass
                
    if not messages_sent:
        print("No messages sent to parent agent found in transcript yet.")
        last_model_content = None
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    step = json.loads(line)
                    if step.get("source") == "MODEL" and step.get("content"):
                        last_model_content = step.get("content")
                except:
                    pass
        if last_model_content:
            print("\n--- Last Model Text (Backup) ---")
            safe_text = last_model_content[:2000].encode('ascii', 'replace').decode('ascii')
            print(safe_text + ("\n... [TRUNCATED] ..." if len(last_model_content) > 2000 else ""))
    else:
        for step_idx, msg in messages_sent:
            print(f"\n--- Message Sent at Step {step_idx} ({len(msg)} chars) ---")
            out_name = name.lower().replace(" ", "_") + "_summary.md"
            out_path = base_dir / "879cc675-1bac-47f1-9b56-8c074e27bd91" / out_name
            try:
                with open(out_path, "w", encoding="utf-8") as out_f:
                    out_f.write(msg)
                print(f"Saved to: {out_name}")
            except Exception as e:
                print(f"Error writing file: {e}")
            
            # Print with ascii replacement to prevent encoding errors on windows terminal
            safe_msg = msg[:3000].encode('ascii', 'replace').decode('ascii')
            print(safe_msg + ("\n... [TRUNCATED] ..." if len(msg) > 3000 else ""))
