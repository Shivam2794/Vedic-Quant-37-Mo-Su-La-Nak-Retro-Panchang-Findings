import asyncio
from playwright.async_api import async_playwright
import http.cookiejar
import os

def load_cookies(filepath):
    cj = http.cookiejar.MozillaCookieJar(filepath)
    cj.load()
    pw_cookies = []
    for c in cj:
        pw_cookies.append({
            "name": c.name,
            "value": c.value,
            "domain": c.domain,
            "path": c.path,
            "secure": c.secure,
            "expires": c.expires
        })
    return pw_cookies

async def main():
    cookies = load_cookies(r'C:\Users\Shivam Patel\Downloads\cookies.txt')
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_cookies(cookies)
        page = await context.new_page()
        
        print("Navigating to classroom...")
        await page.goto("https://www.skool.com/quant-rick/classroom", wait_until="domcontentloaded")
        try:
            await page.wait_for_selector("a[href^='/quant-rick/classroom/']", timeout=10000)
        except:
            print("Could not find course links in time. Maybe logged out or wrong URL?")
            print(await page.content())
            return
            
        print("Finding course links...")
        links = await page.locator("a[href^='/quant-rick/classroom/']").all()
        course_urls = []
        for link in links:
            href = await link.get_attribute("href")
            if href != "/quant-rick/classroom" and href not in course_urls:
                course_urls.append(href)
                
        print(f"Found {len(course_urls)} courses: {course_urls}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
