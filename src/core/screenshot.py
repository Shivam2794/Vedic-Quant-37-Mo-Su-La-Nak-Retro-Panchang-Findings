from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("http://localhost:8555")
    page.wait_for_selector(".bot-card", timeout=10000)
    page.screenshot(path="C:\\Users\\Shivam Patel\\.gemini\\antigravity\\brain\\ff521a99-56df-4cda-af2a-98ca5d5a4471\\dashboard_screenshot.png", full_page=True)
    browser.close()
