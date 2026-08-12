import http.cookiejar
import urllib.request
import json
import os
import subprocess
import time

cookies_path = r'C:\Users\Shivam Patel\Downloads\cookies.txt'
data_path = 'quant_rick_course_data.json'
out_dir = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\quant_rick_videos'

os.makedirs(out_dir, exist_ok=True)

cj = http.cookiejar.MozillaCookieJar(cookies_path)
cj.load()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

with open(data_path, 'r', encoding='utf-8') as f:
    lessons = json.load(f)

print(f"Found {len(lessons)} lessons. Starting download...")

for idx, lesson in enumerate(lessons):
    video_id = lesson.get('video_id')
    # Clean title for filename
    title = lesson.get('lesson_title', f'lesson_{idx+1}')
    valid_chars = "-_.() %s%s" % (chr(255), chr(255))
    clean_title = ''.join(c for c in title if c.isalnum() or c in valid_chars).rstrip()
    
    if not video_id:
        print(f"[{idx+1}/{len(lessons)}] Skipping '{clean_title}' (No video ID)")
        continue
        
    out_path = os.path.join(out_dir, f"{idx+1:02d}_{clean_title}.mp4")
    if os.path.exists(out_path):
        print(f"[{idx+1}/{len(lessons)}] Skipping '{clean_title}' (Already downloaded)")
        continue
        
    print(f"[{idx+1}/{len(lessons)}] Fetching video URL for '{clean_title}'...")
    req = urllib.request.Request(f'https://www.skool.com/api/v1/videos/{video_id}', headers={'User-Agent': 'Mozilla/5.0'})
    try:
        resp = opener.open(req)
        video_data = json.loads(resp.read().decode('utf-8'))
        
        m3u8_url = video_data.get('urls', {}).get('application/vnd.apple.mpegurl')
        
        if not m3u8_url:
            print(f"  -> Error: Could not find m3u8 URL for '{clean_title}'.")
            continue
            
        print(f"  -> Downloading '{clean_title}' via ffmpeg...")
        cmd = [
            "ffmpeg",
            "-y",
            "-i", m3u8_url,
            "-c", "copy",
            out_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"  -> Successfully downloaded to {out_path}")
        time.sleep(1) # Be nice to the server
    except Exception as e:
        print(f"  -> Error fetching/downloading '{clean_title}': {e}")

print(f"\nAll downloads complete! Videos are saved in {out_dir}")
