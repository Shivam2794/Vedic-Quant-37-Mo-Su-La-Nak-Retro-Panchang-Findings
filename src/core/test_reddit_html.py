import sys
import os
sys.path.append(r"C:\Users\Shivam Patel\.gemini\antigravity")
from stealth_scraper.engine import StealthScraper
from bs4 import BeautifulSoup

scraper = StealthScraper()
html = scraper.get_dynamic("https://old.reddit.com/r/algotrading/top/?t=year", max_pages=1)
print("Length of HTML:", len(html))
soup = BeautifulSoup(html, "html.parser")
print("Title of page:", soup.title.text if soup.title else "No Title")
things = soup.find_all("div", class_="thing")
print("Number of div.thing:", len(things))
if things:
    print("Snippet of first thing:", str(things[0])[:500])
else:
    # Print first 2000 chars of body
    body = soup.body
    print("Body snippet:", str(body)[:1000] if body else "No Body")
