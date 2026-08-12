import http.cookiejar, urllib.request, json
cj = http.cookiejar.MozillaCookieJar(r'C:\Users\Shivam Patel\Downloads\cookies.txt')
cj.load()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
req = urllib.request.Request('https://www.skool.com/api/v1/videos/3ff7e2358cb84930ab95db26ed0877cf', headers={'User-Agent': 'Mozilla/5.0'})
try:
    resp = opener.open(req)
    print(resp.read().decode('utf-8'))
except Exception as e:
    print(e)
