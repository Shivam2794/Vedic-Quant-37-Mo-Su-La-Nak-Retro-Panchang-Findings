"""
Re-download the first video (04) which was corrupted and verify it.
Also runs ffprobe verification on all .mp4 files found.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import json
import os
import subprocess
import glob

base_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\quant_rick_channel"

# --- Step 1: re-download corrupted video 04 -----------------------------------
meta_path = os.path.join(base_dir, "Trend-following bootcamp",
                         "04_Welcome to the First Video Introduction_metadata.json")
mp4_path  = os.path.join(base_dir, "Trend-following bootcamp",
                         "04_Welcome to the First Video Introduction.mp4")

with open(meta_path, encoding="utf-8") as f:
    meta = json.load(f)

video = meta.get("video")
if video and video.get("playbackId") and video.get("playbackToken"):
    pid   = video["playbackId"]
    token = video["playbackToken"]
    m3u8  = f"https://stream.video.skool.com/{pid}.m3u8?token={token}"
    print(f"Re-downloading video 04 from:\n  {m3u8}\n")
    # Delete corrupt file first
    if os.path.exists(mp4_path):
        os.remove(mp4_path)
    cmd = [
        "ffmpeg", "-y",
        "-headers", "Referer: https://www.skool.com/",
        "-i", m3u8,
        "-c", "copy",
        mp4_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"[OK]  Re-downloaded successfully: {mp4_path}")
    else:
        print(f"[FAIL]  Download failed:\n{result.stderr[-1000:]}")
else:
    print("[FAIL]  No video playback info found in metadata for video 04!")

# --- Step 2: verify ALL mp4 files found so far --------------------------------
print("\n" + "="*60)
print("VERIFYING ALL DOWNLOADED .mp4 FILES")
print("="*60)

mp4_files = sorted(glob.glob(os.path.join(base_dir, "**", "*.mp4"), recursive=True))
if not mp4_files:
    print("No .mp4 files found yet.")
else:
    ok_count = 0
    bad_count = 0
    for mp4 in mp4_files:
        size_mb = os.path.getsize(mp4) / 1_048_576
        result = subprocess.run(
            ["ffprobe", "-v", "error",
             "-show_entries", "format=duration,size,bit_rate",
             "-show_entries", "stream=codec_name,width,height",
             "-of", "json",
             mp4],
            capture_output=True, text=True
        )
        if result.returncode != 0 or '"format"' not in result.stdout:
            bad_count += 1
            print(f"[FAIL] CORRUPT  [{size_mb:.1f} MB] {os.path.basename(mp4)}")
            print(f"       ffprobe error: {result.stderr.strip()[-300:]}\n")
        else:
            data = json.loads(result.stdout)
            fmt = data.get("format", {})
            duration_s = float(fmt.get("duration", 0))
            duration_mm = int(duration_s // 60)
            duration_ss = int(duration_s % 60)
            streams = data.get("streams", [])
            video_stream = next((s for s in streams if s.get("codec_name") in ("h264","hevc","vp9","av1")), None)
            res = f"{video_stream['width']}x{video_stream['height']}" if video_stream else "audio only"
            ok_count += 1
            print(f"[OK]   [{size_mb:.1f} MB | {duration_mm}m{duration_ss:02d}s | {res}]  {os.path.basename(mp4)}")

    print(f"\n{'='*60}")
    print(f"SUMMARY: {ok_count} OK  |  {bad_count} CORRUPT  |  {len(mp4_files)} total")
    print("="*60)
