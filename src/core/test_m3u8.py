import json
from bs4 import BeautifulSoup
import subprocess

soup = BeautifulSoup(open('skool_course.html', encoding='utf-8'), 'html.parser')
next_data = soup.find('script', id='__NEXT_DATA__')
if next_data:
    data = json.loads(next_data.string)
    render_data = data.get('props', {}).get('pageProps', {}).get('renderData', {})
    
    video = render_data.get('video')
    if video and 'playbackId' in video and 'playbackToken' in video:
        playback_id = video['playbackId']
        token = video['playbackToken']
        
        m3u8_url = f"https://stream.video.skool.com/{playback_id}.m3u8?token={token}"
        print(f"Found M3U8 URL: {m3u8_url}")
        
        print("Testing with ffprobe...")
        subprocess.run(['ffprobe', m3u8_url])
    else:
        print("Video not found in renderData")
else:
    print("No __NEXT_DATA__")
