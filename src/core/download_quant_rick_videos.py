import os
import json
import urllib.request
import http.cookiejar
from bs4 import BeautifulSoup
import subprocess
import time

cookies_path = r'C:\Users\Shivam Patel\Downloads\cookies.txt'
out_dir = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\quant_rick_channel'

os.makedirs(out_dir, exist_ok=True)

print("Loading cookies...")
cj = http.cookiejar.MozillaCookieJar(cookies_path)
cj.load(ignore_discard=True, ignore_expires=True)
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        resp = opener.open(req)
        html = resp.read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        next_data = soup.find('script', id='__NEXT_DATA__')
        if next_data:
            return json.loads(next_data.string)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

print("Fetching classroom data...")
classroom_data = fetch_json("https://www.skool.com/quant-rick/classroom")

if not classroom_data:
    print("Failed to get classroom data.")
    exit(1)

# Skool stores courses in different places depending on the page
page_props = classroom_data.get('props', {}).get('pageProps', {})
render_data = page_props.get('renderData', {})
courses_list = render_data.get('allCourses', []) # array of courses

if not courses_list:
    courses_list = render_data.get('courses', [])

if not courses_list:
    # maybe it's in pageProps.classroom
    classroom = page_props.get('classroom', {})
    courses_list = classroom.get('courses', [])

print(f"Found {len(courses_list)} courses.")

all_modules = []

# Fetch each course to get modules
for c in courses_list:
    course_url = f"https://www.skool.com/quant-rick/classroom/{c.get('name')}"
    print(f"Fetching course: {c.get('title') or c.get('metadata', {}).get('title', 'Unknown')} at {course_url}")
    
    course_page = fetch_json(course_url)
    if not course_page:
        continue
    
    course_render = course_page.get('props', {}).get('pageProps', {}).get('renderData', {})
    course_obj = course_render.get('course', {})
    children = course_obj.get('children', [])
    
    course_title = course_obj.get('course', {}).get('metadata', {}).get('title', 'Unknown_Course')
    valid_chars = "-_.() %s%s" % (chr(255), chr(255))
    clean_course_title = ''.join(char for char in course_title if char.isalnum() or char in valid_chars).rstrip()
    
    course_dir = os.path.join(out_dir, clean_course_title)
    os.makedirs(course_dir, exist_ok=True)
    
    # Save course metadata
    with open(os.path.join(course_dir, 'course_metadata.json'), 'w', encoding='utf-8') as f:
        json.dump(course_obj.get('course', {}), f, indent=2)
        
    print(f"Found {len(children)} modules in course '{course_title}'.")
    
    for idx, child in enumerate(children):
        module = child.get('course', {})
        module_title = module.get('metadata', {}).get('title', f'module_{idx}')
        clean_module_title = ''.join(char for char in module_title if char.isalnum() or char in valid_chars).rstrip()
        
        module_id = module.get('id')
        if not module_id:
            continue
            
        print(f"  Fetching module: {module_title}")
        module_url = f"{course_url}?md={module_id}"
        module_page = fetch_json(module_url)
        if not module_page:
            continue
            
        mod_render = module_page.get('props', {}).get('pageProps', {}).get('renderData', {})
        
        # Save module metadata
        mod_metadata_path = os.path.join(course_dir, f"{idx+1:02d}_{clean_module_title}_metadata.json")
        with open(mod_metadata_path, 'w', encoding='utf-8') as f:
            json.dump(mod_render, f, indent=2)
            
        video = mod_render.get('video')
        if video and 'playbackId' in video and 'playbackToken' in video:
            playback_id = video['playbackId']
            token = video['playbackToken']
            m3u8_url = f"https://stream.video.skool.com/{playback_id}.m3u8?token={token}"
            
            out_path = os.path.join(course_dir, f"{idx+1:02d}_{clean_module_title}.mp4")
            if os.path.exists(out_path):
                print(f"    -> Skipping {clean_module_title}, already exists.")
            else:
                print(f"    -> Downloading video for {clean_module_title}...")
                cmd = [
                    "ffmpeg",
                    "-y",
                    "-headers", "Referer: https://www.skool.com/",
                    "-i", m3u8_url,
                    "-c", "copy",
                    out_path
                ]
                try:
                    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print(f"    -> Successfully downloaded to {out_path}")
                except Exception as e:
                    print(f"    -> Error downloading video: {e}")
        else:
            print(f"    -> No video found for this module.")
            
        time.sleep(1)

print("\nAll complete!")
