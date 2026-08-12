import urllib.request
from bs4 import BeautifulSoup
import re

url = 'https://www.drikpanchang.com/planet/position/planetary-positions-sidereal.html?date=18/11/1999&time=09:30:00'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as response:
    html = response.read().decode('utf-8')

soup = BeautifulSoup(html, 'html.parser')
text = soup.get_text(separator=' | ', strip=True)

for planet in ['Surya', 'Chandra', 'Mangala', 'Budha', 'Guru', 'Shukra', 'Shani', 'Rahu', 'Ketu']:
    idx = text.find(planet)
    if idx != -1:
        print(f"Found {planet}: {text[idx:idx+150]}")
    else:
        print(f"{planet} not found")

for english_planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
    idx = text.find(english_planet)
    if idx != -1:
        print(f"Found {english_planet}: {text[idx:idx+150]}")
