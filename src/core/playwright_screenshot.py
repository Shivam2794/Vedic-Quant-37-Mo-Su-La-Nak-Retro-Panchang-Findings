import asyncio
from playwright.async_api import async_playwright
import http.cookiejar

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
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        await context.add_cookies(cookies)
        page = await context.new_page()
        
        await page.goto("https://www.skool.com/quant-rick/classroom/e5f9d701?md=0a35798918ac4a00b9052e5688236855", wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)
        
        await page.screenshot(path="skool_course.png")
        html = await page.content()
        with open("skool_course.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
