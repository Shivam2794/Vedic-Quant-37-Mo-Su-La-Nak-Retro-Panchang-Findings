import http.cookiejar
import urllib.request

cj = http.cookiejar.MozillaCookieJar(r'C:\Users\Shivam Patel\Downloads\cookies.txt')
cj.load()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
req = urllib.request.Request('https://www.skool.com/quant-rick/classroom/b64df09b?md=9f01d6ec68964cfdb215ca91058947d1', headers={'User-Agent': 'Mozilla/5.0'})
resp = opener.open(req)
html = resp.read().decode('utf-8')

with open('skool_page.html', 'w', encoding='utf-8') as f:
    f.write(html)
