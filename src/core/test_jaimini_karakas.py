import sys
import os

# Ensure we can import jaimini_karakas
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jaimini_karakas import calculate_jaimini_karakas

# Page 2 targets
page_2_targets = [
    {"planet": "Sun", "longitude": 211.626111},
    {"planet": "Moon", "longitude": 186.224167},
    {"planet": "Mars", "longitude": 225.498056},
    {"planet": "Mercury", "longitude": 217.331667},
    {"planet": "Jupiter", "longitude": 90.806111},
    {"planet": "Venus", "longitude": 199.583333},
    {"planet": "Saturn", "longitude": 331.0125},
]

results = calculate_jaimini_karakas(page_2_targets)

for r in results:
    print(f"{r['karaka']} ({r['karaka_abbr']}): {r['planet']} - {r['formatted_degree']}")
