"""
Pipeline Stage 2: Use local llava:13b (vision model via Ollama) to describe
every extracted keyframe. Produces a timestamped visual log per video.
"""
import os
import base64
import json
import requests

frames_base_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\7b03663a-d01b-4302-8959-0a511c484299\frames"
visual_logs_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\7b03663a-d01b-4302-8959-0a511c484299\visual_logs"
os.makedirs(visual_logs_dir, exist_ok=True)

OLLAMA_URL = "http://localhost:11434/api/generate"
VISION_MODEL = "esper-3.1"

VISION_PROMPT = """You are analyzing a frame from a quantitative trading / finance bootcamp video.
Describe EVERYTHING visible in extreme detail:
- If there is a chart (TradingView, price chart): describe the asset, timeframe, all indicators visible, their colors, any crossovers, annotations, marked zones.
- If there is Python code / Jupyter notebook: transcribe the EXACT code visible, including variable names, function names, and all values.
- If there is a whiteboard/slide with text or formulas: transcribe every word, equation, and diagram exactly.
- If there is a browser with research/papers: note the exact title, author, and any visible text.
- If the speaker is talking to camera only: describe what they are gesturing to or pointing at.
Be as literal and precise as possible. Do not interpret — just describe exactly what you see."""

video_labels = [
    "video_04", "video_05", "video_06", "video_07",
    "video_08", "video_09", "video_10", "video_11",
]

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def describe_frame(image_path, frame_num, fps=1/3):
    """Call llava to describe a single frame."""
    timestamp_secs = frame_num * 3  # 1 frame per 3 seconds
    mins = timestamp_secs // 60
    secs = timestamp_secs % 60

    img_b64 = encode_image(image_path)

    payload = {
        "model": VISION_MODEL,
        "prompt": VISION_PROMPT,
        "images": [img_b64],
        "stream": False,
        "options": {
            "temperature": 0.05,
            "num_ctx": 4096,
        }
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    response.raise_for_status()
    description = response.json()["response"].strip()
    return f"[{mins:02d}:{secs:02d}] {description}"

print("=" * 60)
print("STAGE 2: Visual Frame Analysis with llava:13b")
print("=" * 60)

for label in video_labels:
    frame_dir = os.path.join(frames_base_dir, label)
    if not os.path.exists(frame_dir):
        print(f"[SKIP] {label} — frames dir not found")
        continue

    frames = sorted([f for f in os.listdir(frame_dir) if f.endswith(".jpg")])
    if not frames:
        print(f"[SKIP] {label} — no frames found")
        continue

    out_path = os.path.join(visual_logs_dir, label + "_visual_log.txt")
    if os.path.exists(out_path):
        # Check how many frames already processed
        with open(out_path, "r", encoding="utf-8") as f:
            done = f.read().count("\n[")
        if done >= len(frames) - 2:
            print(f"[SKIP] {label} — already processed ({done}/{len(frames)} frames)")
            continue

    print(f"\n[START] Analyzing {len(frames)} frames for {label}...")

    with open(out_path, "w", encoding="utf-8") as out_f:
        out_f.write(f"VISUAL LOG: {label}\n")
        out_f.write(f"Total Frames: {len(frames)} (1 frame per 3 seconds)\n")
        out_f.write("=" * 60 + "\n\n")

        for i, fname in enumerate(frames):
            frame_path = os.path.join(frame_dir, fname)
            frame_num = i + 1

            # Extract frame number from filename (frame_00001.jpg → 1)
            try:
                fn = int(fname.replace("frame_", "").replace(".jpg", ""))
            except:
                fn = frame_num

            try:
                desc = describe_frame(frame_path, fn)
                out_f.write(desc + "\n\n")
                out_f.flush()  # Write immediately so progress is saved
                if i % 20 == 0:
                    print(f"  Progress: {i+1}/{len(frames)} frames done...")
            except Exception as e:
                out_f.write(f"[{fn*3//60:02d}:{fn*3%60:02d}] [ERROR describing frame: {e}]\n\n")

    print(f"[DONE]  {label} visual log saved → {out_path}")

print("\n" + "=" * 60)
print("ALL VISUAL LOGS COMPLETE")
print("=" * 60)
