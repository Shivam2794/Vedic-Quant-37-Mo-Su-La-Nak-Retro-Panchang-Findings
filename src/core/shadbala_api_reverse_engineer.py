import requests
import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

# Ensure we can import our engine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from vedic_engine_core import VedicAstrologyEngine

API_KEY = "RznpdHVUz123T19CLGRHg2NXZ2DFmTaH9eb6Eb1P"
HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

# SPY Trading Date
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

print("Fetching API Shadbala Break-up...")
url = "https://json.freeastrologyapi.com/shadbala/break-up"
res = requests.post(url, json=payload, headers=HEADERS)

if res.status_code != 200:
    print(f"API Error: {res.status_code} {res.text}")
    sys.exit(1)

api_data = res.json()["output"]

print("Computing Internal Shadbala (BPHS Pure)...")
from shadbala_core import calc_shadbala

engine = VedicAstrologyEngine(lat=40.7128, lon=-74.0060, tz='America/New_York')
jd, dt_utc = engine.get_jd("1993-01-29 09:30:00")
planets = engine.calculate_d1(jd)

# Asc/MC are not stored in planets dict directly, but we can compute or extract them
import swisseph as swe
flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH | swe.FLG_SPEED
houses, ascmc = swe.houses_ex(jd, 40.7128, -74.0060, b'W', flags)
asc_lon, mc_lon = ascmc[0], ascmc[1]
sun_lon = planets["Sun"]["longitude"]
moon_lon = planets["Moon"]["longitude"]

our_shadbala = calc_shadbala(planets, asc_lon, sun_lon, moon_lon, jd, mc_lon)


print("\n" + "="*80)
print(f"{'Planet':<10} | {'Component':<15} | {'API Value':<15} | {'Our Value':<15} | {'Diff / Multiplier'}")
print("="*80)

pillars_map = {
    "sthana": "Sthana",
    "kaala": "Kaala",
    "dig_balam": "Dig",
    "chesta": "Chesta",
    "drik_balam": "Drik",
    "naisargika": "Naisargika"
}

for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
    api_p = api_data.get(planet, {})
    our_p = our_shadbala.get(planet, {}).get("breakdown", {})
    
    for api_k, our_k in pillars_map.items():
        api_v = float(api_p.get(api_k, 0))
        our_v = float(our_p.get(our_k, 0))
        
        diff = api_v - our_v
        mult = (api_v / our_v) if our_v != 0 else 0
        
        if abs(diff) > 1.0:
            flag = "🚨"
        elif abs(diff) > 0.1:
            flag = "⚠️ "
        else:
            flag = "✅"
            
        print(f"{planet:<10} | {our_k:<15} | {api_v:<15.3f} | {our_v:<15.3f} | {flag} {diff:+.3f} (x{mult:.2f})")
    print("-" * 80)
