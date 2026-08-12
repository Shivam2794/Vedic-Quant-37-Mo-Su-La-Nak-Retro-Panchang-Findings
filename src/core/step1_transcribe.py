"""
Pipeline Step 1: Transcribe all downloaded Skool videos using Whisper (local, runs on GPU/CPU).
Saves timestamped transcripts to the transcripts/ folder.
"""
import whisper
import os
import json

video_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
transcript_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\7b03663a-d01b-4302-8959-0a511c484299\transcripts"
os.makedirs(transcript_dir, exist_ok=True)

# All videos that need transcription (Videos 4-11 downloaded, 12-13 unknown)
videos = [
    "skool_video_03.mp4",   # Video 4
    "skool_video_04.mp4",   # Video 5
    "skool_video_05.mp4",   # Video 6
    "skool_video_06.mp4",   # Video 7
    "skool_video_07.mp4",   # Video 8
    "skool_video_08.mp4",   # Video 9
    "skool_video_09.mp4",   # Video 10
    "skool_video_10.mp4",   # Video 11
]

print("=" * 60)
print("WHISPER BATCH TRANSCRIPTION - Quant Bootcamp Videos")
print("=" * 60)
print("Loading Whisper 'small' model (good accuracy + speed)...")
model = whisper.load_model("small")
print("Model loaded successfully.\n")

for video in videos:
    video_path = os.path.join(video_dir, video)
    if not os.path.exists(video_path):
        print(f"[SKIP] {video} — file not found.")
        continue

    name = os.path.splitext(video)[0]
    txt_out = os.path.join(transcript_dir, name + "_transcript.txt")
    json_out = os.path.join(transcript_dir, name + "_transcript.json")

    if os.path.exists(txt_out):
        print(f"[SKIP] {video} — already transcribed.")
        continue

    file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
    print(f"[START] Transcribing {video} ({file_size_mb:.1f} MB)...")

    result = model.transcribe(
        video_path,
        verbose=False,
        language="en",
        task="transcribe",
        word_timestamps=False,
    )

    # Save full JSON for later processing
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Save human-readable timestamped transcript
    with open(txt_out, "w", encoding="utf-8") as f:
        f.write(f"TRANSCRIPT: {video}\n")
        f.write("=" * 60 + "\n\n")
        for seg in result["segments"]:
            mins = int(seg['start']) // 60
            secs = int(seg['start']) % 60
            f.write(f"[{mins:02d}:{secs:02d}] {seg['text'].strip()}\n")

    word_count = len(result["text"].split())
    print(f"[DONE]  {video} — {word_count} words transcribed → {txt_out}")

print("\n" + "=" * 60)
print("ALL TRANSCRIPTIONS COMPLETE.")
print("=" * 60)
