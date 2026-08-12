import sys
import os
sys.path.append(r"C:\Users\Shivam Patel\.gemini\antigravity")
from stealth_scraper.engine import StealthScraper
from bs4 import BeautifulSoup

scraper = StealthScraper()
html = scraper.get_dynamic("https://old.reddit.com/search?q=working+strategy+beating+qqq&sort=top&t=year", max_pages=1)
print("Length of HTML:", len(html))
soup = BeautifulSoup(html, "html.parser")
print("Title of page:", soup.title.text if soup.title else "No Title")
# search for all links that have "search" in class or "title" in class
links = soup.find_all("a")
print("Total links:", len(links))
for l in links[:50]:
    c = l.get('class', [])
    if c:
        print(f"Link text: {l.text.strip()[:50]} | Class: {c} | Href: {l.get('href')}")
