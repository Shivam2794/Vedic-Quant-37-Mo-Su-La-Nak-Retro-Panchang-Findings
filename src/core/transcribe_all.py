import whisper
import os
import sys

video_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
transcript_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\7b03663a-d01b-4302-8959-0a511c484299\transcripts"
os.makedirs(transcript_dir, exist_ok=True)

# Videos that still need transcription (already did 01, 02, 03 manually)
videos = [
    "skool_video_03.mp4",
    "skool_video_04.mp4",
    "skool_video_05.mp4",
    "skool_video_06.mp4",
    "skool_video_07.mp4",
    "skool_video_08.mp4",
    "skool_video_09.mp4",
    "skool_video_10.mp4",
]

print("Loading Whisper model (base)...")
model = whisper.load_model("base")
print("Model loaded.")

for video in videos:
    video_path = os.path.join(video_dir, video)
    if not os.path.exists(video_path):
        print(f"SKIP: {video} not found.")
        continue
    name = os.path.splitext(video)[0]
    out_path = os.path.join(transcript_dir, name + "_transcript.txt")
    if os.path.exists(out_path):
        print(f"SKIP: {video} already transcribed.")
        continue
    print(f"\nTranscribing {video} ...")
    result = model.transcribe(video_path, verbose=False)
    with open(out_path, "w", encoding="utf-8") as f:
        for seg in result["segments"]:
            ts = f"[{seg['start']:.1f}s - {seg['end']:.1f}s]"
            f.write(f"{ts} {seg['text'].strip()}\n")
    print(f"Done: {out_path}")

print("\nAll transcriptions complete.")
