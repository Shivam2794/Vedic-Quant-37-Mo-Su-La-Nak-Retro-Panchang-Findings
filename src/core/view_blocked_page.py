import sys
import os
sys.path.append(r"C:\Users\Shivam Patel\.gemini\antigravity")
from stealth_scraper.engine import StealthScraper
from bs4 import BeautifulSoup

scraper = StealthScraper()
html = scraper.get_dynamic("https://old.reddit.com/search?q=working+strategy+beating+qqq&sort=top&t=year", max_pages=1)
soup = BeautifulSoup(html, "html.parser")
print(soup.get_text()[:2000])
