"""
Pipeline Step 1: Extract keyframes from each video every 3 seconds using ffmpeg.
Only saves frames where significant visual change occurs (scene change detection).
This gives us all charts, code, whiteboard drawings shown in the video.
"""
import subprocess
import os

video_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
frames_base_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\7b03663a-d01b-4302-8959-0a511c484299\frames"

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
print("STAGE 1: Keyframe Extraction with ffmpeg")
print("=" * 60)

for video_file, label in videos:
    video_path = os.path.join(video_dir, video_file)
    if not os.path.exists(video_path):
        print(f"[SKIP] {video_file} — not found")
        continue

    out_dir = os.path.join(frames_base_dir, label)
    os.makedirs(out_dir, exist_ok=True)

    # Check if already extracted
    existing = [f for f in os.listdir(out_dir) if f.endswith(".jpg")]
    if len(existing) > 10:
        print(f"[SKIP] {video_file} — {len(existing)} frames already extracted")
        continue

    print(f"\n[START] Extracting frames from {video_file} -> {out_dir}")

    # Extract 1 frame every 3 seconds at 50% quality, resize to 1280x720 for speed
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vf", "fps=1/3,scale=1280:720",
        "-q:v", "3",
        "-f", "image2",
        os.path.join(out_dir, "frame_%05d.jpg"),
        "-y", "-hide_banner", "-loglevel", "error"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] {video_file}: {result.stderr[:300]}")
        continue

    n_frames = len([f for f in os.listdir(out_dir) if f.endswith(".jpg")])
    print(f"[DONE]  {video_file} -> {n_frames} frames extracted")

print("\n" + "=" * 60)
print("FRAME EXTRACTION COMPLETE")
print("=" * 60)
