import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import json, urllib.request, http.cookiejar
from bs4 import BeautifulSoup

cj = http.cookiejar.MozillaCookieJar(r'C:\Users\Shivam Patel\Downloads\cookies.txt')
cj.load(ignore_discard=True, ignore_expires=True)
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
req = urllib.request.Request('https://www.skool.com/quant-rick/classroom/e5f9d701', headers={'User-Agent': 'Mozilla/5.0'})
resp = opener.open(req)
html = resp.read().decode('utf-8')
soup = BeautifulSoup(html, 'html.parser')
data = json.loads(soup.find('script', id='__NEXT_DATA__').string)
rd = data['props']['pageProps']['renderData']
course = rd.get('course', {})
children = course.get('children', [])
title = course.get('course', {}).get('metadata', {}).get('title', 'N/A')
print(f"Course: {title}")
print(f"Modules: {len(children)}")
for i, c in enumerate(children):
    m = c.get('course', {}).get('metadata', {})
    vid = m.get('videoId', 'none')
    print(f"  {i+1}. {m.get('title','?')} | videoId={vid}")
