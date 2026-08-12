import http.cookiejar
import urllib.request
import json
from bs4 import BeautifulSoup
import os

url = 'https://www.skool.com/quant-rick/classroom/e5f9d701?md=0a35798918ac4a00b9052e5688236855'
cookies_path = r'C:\Users\Shivam Patel\Downloads\cookies.txt'

def parse_skool_description(desc_str):
    """Attempt to extract plain text from Skool's rich text description JSON format."""
    if not desc_str: return ""
    try:
        if desc_str.startswith('[v2]'):
            json_str = desc_str[4:]
            data = json.loads(json_str)
            text = ""
            for block in data:
                if block.get('type') == 'paragraph':
                    for content in block.get('content', []):
                        if content.get('type') == 'text':
                            text += content.get('text', '')
                    text += "\n\n"
                elif block.get('type') == 'heading':
                    for content in block.get('content', []):
                        if content.get('type') == 'text':
                            text += content.get('text', '')
                    text += "\n\n"
            return text.strip()
    except Exception:
        pass
    return desc_str

def main():
    if not os.path.exists(cookies_path):
        print(f"Error: cookies.txt not found at {cookies_path}")
        return

    cj = http.cookiejar.MozillaCookieJar(cookies_path)
    cj.load()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    print("Fetching page...")
    resp = opener.open(req)
    html = resp.read().decode('utf-8')
    
    soup = BeautifulSoup(html, 'html.parser')
    next_data_tag = soup.find('script', id='__NEXT_DATA__')
    
    if not next_data_tag:
        print("Error: Could not find __NEXT_DATA__ in the page.")
        return
        
    data = json.loads(next_data_tag.string)
    
    course_root = data.get('props', {}).get('pageProps', {}).get('course', {})
    children = course_root.get('children', [])
    
    results = []
    
    print(f"Found {len(children)} lessons in the course.")
    
    for child in children:
        course_data = child.get('course', {})
        metadata = course_data.get('metadata', {})
        
        title = metadata.get('title', 'Unknown Lesson')
        desc_raw = metadata.get('desc', '')
        desc = parse_skool_description(desc_raw)
        video_id = metadata.get('videoId', '')
        
        # Resources / Attachments
        resources = []
        res_raw = metadata.get('resources')
        if res_raw and res_raw != "[]":
            try:
                res_data = json.loads(res_raw)
                for r in res_data:
                    res_url = r.get('url', '')
                    res_name = r.get('name', 'Attachment')
                    if res_url:
                        resources.append(f"{res_name} ({res_url})")
            except:
                resources.append(str(res_raw))
        
        results.append({
            "lesson_title": title,
            "description": desc,
            "video_id": video_id,
            "resources": resources
        })
            
    print(f"Extracted {len(results)} lessons.")
    
    with open('quant_rick_course_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
        
    with open('quant_rick_course_data.txt', 'w', encoding='utf-8') as f:
        for idx, r in enumerate(results):
            f.write(f"Lesson {idx + 1}: {r['lesson_title']}\n")
            f.write(f"Video ID: {r['video_id']}\n")
            if r['resources']:
                f.write(f"Resources: {', '.join(r['resources'])}\n")
            f.write(f"Description:\n{r['description']}\n")
            f.write("-" * 60 + "\n\n")
            
    print("Saved successfully to quant_rick_course_data.json and quant_rick_course_data.txt")

if __name__ == "__main__":
    main()
