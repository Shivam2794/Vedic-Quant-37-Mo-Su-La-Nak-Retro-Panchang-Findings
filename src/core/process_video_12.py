import os
import subprocess
import json
import whisper
import requests

video_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
brain_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\7b03663a-d01b-4302-8959-0a511c484299"
frames_dir = os.path.join(brain_dir, "frames", "video_12")
transcript_dir = os.path.join(brain_dir, "transcripts")

os.makedirs(frames_dir, exist_ok=True)
os.makedirs(transcript_dir, exist_ok=True)

video_file = "skool_video_12.mp4"
video_path = os.path.join(video_dir, video_file)

print(f"Checking {video_path}...")
if not os.path.exists(video_path):
    print("Video 12 not found. Exiting.")
    exit(1)

# Step 1: Extract Frames
print("Extracting frames...")
cmd = [
    "ffmpeg", "-i", video_path,
    "-vf", "select='gt(scene,0.03)',setpts=N/FRAME_RATE/TB",
    "-vsync", "vfr",
    "-frame_pts", "true",
    os.path.join(frames_dir, "frame_%05d.jpg")
]
subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("Frames extracted.")

# Step 2: Extract Audio and Transcribe
print("Extracting audio and transcribing...")
model = whisper.load_model("small")
result = model.transcribe(video_path)

transcript_path = os.path.join(transcript_dir, "video_12.json")
with open(transcript_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=4)
print(f"Transcript saved to {transcript_path}")

# Step 3: Draft Report using Ollama
print("Drafting report using Ollama esper-3.1...")
full_text = "\n".join([segment["text"] for segment in result["segments"]])
prompt = f"""You are a senior quantitative analyst. You have just read a complete transcript of a video lecture from a Quant trading bootcamp.

Your job is to write an EXHAUSTIVE, DETAILED, WORD-BY-WORD report of the video. You must:
1. Document EVERY single concept, formula, strategy rule, code snippet, and reference mentioned.
2. Preserve EXACT quotes where possible.
3. Structure the report with clear numbered sections for each topic discussed.
4. Note every chart, visual, or code demo shown (describe it precisely).
5. Highlight every strategy parameter.
6. Do NOT summarize or skip anything. Length is a virtue here. Be comprehensive.

Transcript:
{full_text}
"""

try:
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "esper-3.1",
        "prompt": prompt,
        "stream": False,
        "options": {"num_ctx": 32000}
    })
    response.raise_for_status()
    draft = response.json()["response"]
    
    draft_path = os.path.join(brain_dir, "video_12_draft_report.md")
    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(draft)
    print(f"Draft report saved to {draft_path}")
except Exception as e:
    print(f"Ollama failed: {e}")

print("Processing complete!")
