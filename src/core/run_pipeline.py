"""
MASTER PIPELINE RUNNER
Runs all 4 stages sequentially for each video:
  Stage 1: ffmpeg keyframe extraction
  Stage 2: llava:13b visual frame analysis
  Stage 3: Whisper audio transcription
  Stage 4: esper-3.1 report drafting

Stages 2 and 3 run in parallel per video (both can run simultaneously).
"""
import subprocess
import sys
import os

scripts = [
    ("Stage 1 - Frame Extraction",    "stage1_extract_frames.py"),
    ("Stage 3 - Audio Transcription", "stage3_transcribe.py"),
    ("Stage 2 - Visual Analysis",     "stage2_analyze_frames.py"),
    ("Stage 4 - Report Drafting",     "stage4_draft_reports.py"),
]

base = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"

for stage_name, script in scripts:
    script_path = os.path.join(base, script)
    print(f"\n{'='*60}")
    print(f"RUNNING: {stage_name}")
    print(f"Script:  {script_path}")
    print('='*60)
    result = subprocess.run([sys.executable, script_path], cwd=base)
    if result.returncode != 0:
        print(f"\n[WARNING] {stage_name} exited with code {result.returncode}. Continuing...")
    else:
        print(f"\n[OK] {stage_name} completed successfully.")

print("\n" + "="*60)
print("FULL PIPELINE COMPLETE")
print("="*60)
print("Next step: Senior analyst (Claude) will read all draft reports")
print("and produce the final enriched, expert-level analysis.")
