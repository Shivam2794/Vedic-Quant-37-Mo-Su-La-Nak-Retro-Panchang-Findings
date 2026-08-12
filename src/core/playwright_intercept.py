import asyncio
from playwright.async_api import async_playwright
import http.cookiejar
import json
import urllib.parse

def load_cookies(filepath):
    cj = http.cookiejar.MozillaCookieJar(filepath)
    cj.load(ignore_discard=True, ignore_expires=True)
    pw_cookies = []
    for c in cj:
        if "skool" in c.domain:
            domain = c.domain if c.domain.startswith('.') else '.' + c.domain
            pw_cookies.append({
                "name": c.name,
                "value": c.value,
                "domain": domain,
                "path": c.path,
                "secure": c.secure
            })
    return pw_cookies

async def main():
    cookies = load_cookies(r'C:\Users\Shivam Patel\Downloads\cookies.txt')
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_cookies(cookies)
        page = await context.new_page()
        
        video_urls = []
        page.on("request", lambda request: video_urls.append(request.url) if ".m3u8" in request.url or "stream.video.skool.com" in request.url or "loom.com/embed" in request.url or "vimeo" in request.url or "wistia" in request.url else None)
        
        print("Navigating to course module...")
        await page.goto("https://www.skool.com/quant-rick/classroom/e5f9d701?md=0a35798918ac4a00b9052e5688236855", wait_until="domcontentloaded")
        
        print("Waiting a bit for video to load...")
        await page.wait_for_timeout(5000)
        
        print("Found video urls:")
        for v in video_urls:
            print(v)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
