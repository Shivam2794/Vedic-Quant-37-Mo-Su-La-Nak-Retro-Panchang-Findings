import urllib.request
import http.cookiejar
from bs4 import BeautifulSoup
import json

COOKIES_PATH = r'C:\Users\Shivam Patel\Downloads\cookies.txt'
URL = 'https://www.skool.com/quant-rick/classroom'

cj = http.cookiejar.MozillaCookieJar(COOKIES_PATH)
cj.load(ignore_discard=True, ignore_expires=True)
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

req = urllib.request.Request(URL, headers=HEADERS)
resp = opener.open(req)
html = resp.read().decode('utf-8')
soup = BeautifulSoup(html, 'html.parser')
tag = soup.find('script', id='__NEXT_DATA__')
if tag:
    data = json.loads(tag.string)
    courses = data.get('props', {}).get('pageProps', {}).get('renderData', {}).get('courses', [])
    print(f'Found {len(courses)} courses.')
    for c in courses:
        meta = c.get('course', {}).get('metadata', {})
        print(f"- {c.get('course', {}).get('name')}: {meta.get('title')}")
else:
    print('No NEXT DATA found')
