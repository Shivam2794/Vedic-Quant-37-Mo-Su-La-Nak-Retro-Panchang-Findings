import os
import json
import urllib.request
import http.cookiejar
from bs4 import BeautifulSoup
import subprocess
import time

COOKIES_PATH = r'C:\Users\Shivam Patel\Downloads\cookies.txt'
OUT_DIR      = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\quant_rick_channel'

COURSES = [
    'c0fab865', # Q&A's
]

os.makedirs(OUT_DIR, exist_ok=True)

print('Loading cookies...', flush=True)
cj = http.cookiejar.MozillaCookieJar(COOKIES_PATH)
cj.load(ignore_discard=True, ignore_expires=True)
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        resp = opener.open(req, timeout=30)
        html = resp.read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        tag  = soup.find('script', id='__NEXT_DATA__')
        if tag:
            return json.loads(tag.string)
    except Exception as e:
        print(f'  [ERROR] fetching {url}: {e}', flush=True)
    return None

def safe(name):
    keep = set(' -_.()abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    return ''.join(c if c in keep else '_' for c in name).strip()

def plain_desc(raw):
    try:
        blob = json.loads(raw[4:] if raw.startswith('[v2]') else raw)
        parts = []
        def walk(node):
            if isinstance(node, dict):
                if node.get('type') == 'text':
                    parts.append(node.get('text', ''))
                for v in node.values():
                    if isinstance(v, (dict, list)):
                        walk(v)
            elif isinstance(node, list):
                for item in node:
                    walk(item)
        walk(blob)
        return ' '.join(parts).strip()
    except Exception:
        return raw

def download_course(course_id):
    base_url = f'https://www.skool.com/quant-rick/classroom/{course_id}'
    print(f'\n\n{"="*80}\nFetching course: {base_url}\n{"="*80}', flush=True)
    data = fetch(base_url)
    if not data:
        print(f'ERROR: could not load course page {course_id}.', flush=True)
        return

    rd       = data.get('props', {}).get('pageProps', {}).get('renderData', {})
    course   = rd.get('course', {})
    children = course.get('children', [])
    title    = course.get('course', {}).get('metadata', {}).get('title', 'Unknown')

    print(f'Course title : {title}', flush=True)
    print(f'Total modules: {len(children)}', flush=True)

    course_dir = os.path.join(OUT_DIR, safe(title))
    os.makedirs(course_dir, exist_ok=True)

    with open(os.path.join(course_dir, 'course_metadata.json'), 'w', encoding='utf-8') as f:
        json.dump(course, f, indent=2, ensure_ascii=False)

    ok_count    = 0
    skip_count  = 0
    noVid_count = 0
    fail_count  = 0

    for idx, child in enumerate(children):
        mod_meta  = child.get('course', {}).get('metadata', {})
        mod_id    = child.get('course', {}).get('id', '')
        mod_title = mod_meta.get('title', f'module_{idx+1}')
        safe_t    = safe(mod_title)

        num = f'{idx+1:02d}'
        print(f'\n[{num}/{len(children):02d}] {mod_title}', flush=True)

        mod_url  = f'{base_url}?md={mod_id}'
        mod_data = fetch(mod_url)
        if not mod_data:
            print('  -> Could not load module page, skipping.', flush=True)
            fail_count += 1
            time.sleep(1)
            continue

        mod_rd = mod_data.get('props', {}).get('pageProps', {}).get('renderData', {})

        meta_file = os.path.join(course_dir, f'{num}_{safe_t}_metadata.json')
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(mod_rd, f, indent=2, ensure_ascii=False)

        desc_raw = mod_rd.get('course', {}).get('course', {}).get('metadata', {}).get('desc', '')
        if not desc_raw:
            v2_list = []
            def find_v2(node):
                if isinstance(node, str) and node.startswith('[v2]'):
                    v2_list.append(node)
                elif isinstance(node, dict):
                    for v in node.values(): find_v2(v)
                elif isinstance(node, list):
                    for item in node: find_v2(item)
            find_v2(mod_rd)
            if v2_list:
                desc_raw = v2_list[0]
                
        desc_txt = plain_desc(desc_raw)
        desc_file = os.path.join(course_dir, f'{num}_{safe_t}_description.txt')
        with open(desc_file, 'w', encoding='utf-8') as f:
            f.write(f'{mod_title}\n{"="*len(mod_title)}\n\n{desc_txt}\n')
        print(f'  Description: {desc_txt[:120]}...', flush=True)

        video = mod_rd.get('video')
        if not video or not video.get('playbackId') or not video.get('playbackToken'):
            print('  -> No video (text/resource only).', flush=True)
            noVid_count += 1
            time.sleep(0.5)
            continue

        pid   = video['playbackId']
        token = video['playbackToken']
        m3u8  = f'https://stream.video.skool.com/{pid}.m3u8?token={token}'
        mp4   = os.path.join(course_dir, f'{num}_{safe_t}.mp4')

        if os.path.exists(mp4) and os.path.getsize(mp4) > 1_000_000:
            chk = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'json', mp4],
                capture_output=True, text=True
            )
            if chk.returncode == 0 and '"format"' in chk.stdout:
                size_mb = os.path.getsize(mp4) / 1_048_576
                print(f'  -> Already exists and is valid ({size_mb:.1f} MB), skipping.', flush=True)
                skip_count += 1
                time.sleep(0.5)
                continue
            else:
                print(f'  -> Exists but is CORRUPT, deleting and re-downloading...', flush=True)
                os.remove(mp4)

        print(f'  -> Downloading...', flush=True)
        cmd = ['ffmpeg', '-y', '-headers', 'Referer: https://www.skool.com/',
               '-i', m3u8, '-c', 'copy', mp4]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            size_mb = os.path.getsize(mp4) / 1_048_576
            print(f'  -> [DONE] {size_mb:.1f} MB -> {os.path.basename(mp4)}', flush=True)
            ok_count += 1
        else:
            print(f'  -> [FAIL] ffmpeg error (last 300 chars):\n{res.stderr[-300:]}', flush=True)
            fail_count += 1

        time.sleep(1)

    print(f'\nFINISHED {title}: {ok_count} downloaded | {skip_count} skipped | {noVid_count} text-only | {fail_count} failed', flush=True)

for cid in COURSES:
    download_course(cid)
