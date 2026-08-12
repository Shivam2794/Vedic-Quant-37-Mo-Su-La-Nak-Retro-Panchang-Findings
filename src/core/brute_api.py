import requests
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

paths = [
    "shadbala",
    "shad-bala",
    "shadbala-summary",
    "shadbala_summary",
    "shadbala/summary",
    "shadbala-break-up",
    "shadbala_break_up",
    "shadbala/break-up",
    "shadbala/shadbala-summary",
    "shadbala/shadbala-break-up",
    "sthana-bala",
    "kaala-bala",
    "dig-bala",
    "cheshta-bala",
    "drig-bala",
    "naisargika-bala",
    "shadbala/sthana-bala"
]

for p in paths:
    url = f"https://json.freeastrologyapi.com/{p}"
    res = requests.post(url, json=payload, headers=HEADERS)
    if res.status_code == 200:
        print(f"✅ SUCCESS: {url}")
        print(res.text[:200])
    else:
        # Ignore 403 Missing Authentication Token since it means route not found
        if "Missing Authentication Token" not in res.text:
            print(f"❌ Failed ({res.status_code}): {url} -> {res.text[:100]}")
