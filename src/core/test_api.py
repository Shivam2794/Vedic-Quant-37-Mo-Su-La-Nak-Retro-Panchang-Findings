import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "RznpdHVUz123T19CLGRHg2NXZ2DFmTaH9eb6Eb1P"
HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "year": 1993,
    "month": 1,
    "date": 29,
    "hours": 9,
    "minutes": 30,
    "seconds": 0,
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": -5.0,
    "settings": {
        "ayanamsha": "lahiri"
    }
}

endpoints = [
    "https://json.freeastrologyapi.com/shadbala/shadbala-summary",
    "https://json.freeastrologyapi.com/shadbala/shadbala-break-up",
    "https://json.freeastrologyapi.com/shadbala-break-up"
]

for url in endpoints:
    print(f"Testing {url}...")
    res = requests.post(url, json=payload, headers=HEADERS)
    if res.status_code == 200:
        print("Success JSON:", json.dumps(res.json(), indent=2)[:300] + "...\n")
    else:
        print(f"Failed: {res.status_code} {res.text}")
