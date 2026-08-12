"""
Pipeline Stage 3: Transcribe audio from each video using Whisper (local).
Produces timestamped word-for-word transcripts.
"""
import whisper
import os
import json

video_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
transcript_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\7b03663a-d01b-4302-8959-0a511c484299\transcripts"
os.makedirs(transcript_dir, exist_ok=True)

videos = [
    ("skool_video_03.mp4", "video_04"),
    ("skool_video_04.mp4", "video_05"),
    ("skool_video_05.mp4", "video_06"),
    ("skool_video_06.mp4", "video_07"),
    ("skool_video_07.mp4", "video_08"),
    ("skool_video_08.mp4", "video_09"),
    ("skool_video_09.mp4", "video_10"),
    ("skool_video_10.mp4", "video_11"),
]

print("=" * 60)
print("STAGE 3: Audio Transcription with Whisper (small model)")
print("=" * 60)
print("Loading Whisper 'small' model...")
model = whisper.load_model("small")
print("Model loaded.\n")

for video_file, label in videos:
    video_path = os.path.join(video_dir, video_file)
    if not os.path.exists(video_path):
        print(f"[SKIP] {video_file} — not found")
        continue

    txt_out = os.path.join(transcript_dir, label + "_transcript.txt")
    if os.path.exists(txt_out):
        print(f"[SKIP] {video_file} — transcript already exists")
        continue

    size_mb = os.path.getsize(video_path) / 1024 / 1024
    print(f"[START] Transcribing {video_file} ({size_mb:.1f} MB)...")

    result = model.transcribe(
        video_path,
        verbose=False,
        language="en",
        task="transcribe",
    )

    with open(txt_out, "w", encoding="utf-8") as f:
        f.write(f"TRANSCRIPT: {label} ({video_file})\n")
        f.write("=" * 60 + "\n\n")
        for seg in result["segments"]:
            mins = int(seg['start']) // 60
            secs = int(seg['start']) % 60
            f.write(f"[{mins:02d}:{secs:02d}] {seg['text'].strip()}\n")

    words = len(result["text"].split())
    print(f"[DONE]  {video_file} - {words} words -> {txt_out}")

print("\n" + "=" * 60)
print("ALL TRANSCRIPTIONS COMPLETE")
print("=" * 60)
