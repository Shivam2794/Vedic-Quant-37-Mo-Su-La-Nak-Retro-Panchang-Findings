import json, re
html = open('skool_page.html', encoding='utf-8').read()
match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    
    # recursively search for anything looking like a video URL or wistia ID
    def find_video_urls(obj):
        urls = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, str) and ('wistia.com' in v or 'vimeo.com' in v or 'mux.com' in v or 'vimeo' in k.lower() or 'wistia' in k.lower() or 'video' in k.lower() or 'url' in k.lower()):
                    urls.append(f"{k}: {v}")
                elif isinstance(v, (dict, list)):
                    urls.extend(find_video_urls(v))
        elif isinstance(obj, list):
            for item in obj:
                urls.extend(find_video_urls(item))
        return urls

    found = find_video_urls(data)
    for f in set(found):
        print(f)
else:
    print("Could not find __NEXT_DATA__")
