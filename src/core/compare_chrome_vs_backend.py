import json
import swisseph as swe
from datetime import datetime
import pytz

swe.set_ephe_path(None)
swe.set_sid_mode(swe.SIDM_LAHIRI)

PLANET_IDS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE
}
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigasira","Ardra","Punarvasu","Pushya","Ashlesha",
    "Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha",
    "Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"
]

def dms(lon):
    sign_idx = int(lon / 30) % 12
    deg_in_sign = lon % 30
    deg = int(deg_in_sign)
    mins = int((deg_in_sign - deg) * 60)
    secs = int(((deg_in_sign - deg) * 60 - mins) * 60)
    return SIGNS[sign_idx], deg, mins, secs

def calc_full(dt_string):
    ny_tz = pytz.timezone('America/New_York')
    dt_naive = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
    dt_ny = ny_tz.localize(dt_naive)
    dt_utc = dt_ny.astimezone(pytz.utc)
    utc_hour = dt_utc.hour + (dt_utc.minute / 60.0) + (dt_utc.second / 3600.0)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, utc_hour)

    flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH
    results = {}
    pos_raw = {}

    for p_name, p_id in PLANET_IDS.items():
        res = swe.calc_ut(jd, p_id, flags)
        lon = res[0][0]
        speed = res[0][3]
        retro = speed < 0
        pos_raw[p_name] = lon
        sign, d, m, s = dms(lon)
        results[p_name] = f"{sign} {d:02d}° {m:02d}' {s:02d}\" {'(R)' if retro else ''}"

    ketu_lon = (pos_raw["Rahu"] + 180.0) % 360.0
    pos_raw["Ketu"] = ketu_lon
    sign, d, m, s = dms(ketu_lon)
    results["Ketu"] = f"{sign} {d:02d}° {m:02d}' {s:02d}\""

    # Ascendant
    houses, ascmc = swe.houses_ex(jd, 40.7128, -74.0060, b'W', flags)
    asc_lon = ascmc[0]
    sign, d, m, s = dms(asc_lon)
    results["Ascendant"] = f"{sign} {d:02d}° {m:02d}' {s:02d}\""

    # D9 Navamsa
    d9 = {}
    for p, lon in {**pos_raw, "Ascendant": asc_lon}.items():
        navamsa_idx = int(lon / (10.0/3.0)) % 12
        d9[p] = SIGNS[navamsa_idx]

    # D10 Dasamsa
    d10 = {}
    for p, lon in {**pos_raw, "Ascendant": asc_lon}.items():
        sign_idx = int(lon / 30)
        part_idx = int((lon % 30) / 3.0)
        if sign_idx % 2 == 0:
            d10[p] = SIGNS[(sign_idx + part_idx) % 12]
        else:
            d10[p] = SIGNS[(sign_idx + 8 + part_idx) % 12]

    # Nakshatra of Moon
    moon_lon = pos_raw["Moon"]
    nak_idx = int(moon_lon / (360/27))
    moon_nak = NAKSHATRAS[nak_idx]

    return {"D1": results, "D9": d9, "D10": d10, "Moon_Nakshatra": moon_nak}


# ===== KEY DATES TO CROSS-VERIFY FROM CHROME AGENT =====
TEST_CASES = {
    "Sector_ETFs_Conception": "1998-12-16 12:00:00",
    "Sector_ETFs_Trading":    "1998-12-22 09:30:00",
    "XLRE_Conception":        "2015-10-06 12:00:00",
    "XLRE_Trading":           "2015-10-08 09:30:00",
    "XLC_Conception":         "2018-06-18 12:00:00",
    "XLC_Trading":            "2018-06-19 09:30:00",
    "SMH_Conception":         "2000-12-18 12:00:00",
    "SMH_Trading":            "2000-12-20 09:30:00",
    "XME_Conception":         "2006-06-19 12:00:00",
    "Transit_2024-11-05":     "2024-11-05 12:00:00",
    "Transit_2025-02-10":     "2025-02-10 12:00:00",
    "Transit_2027-02-10":     "2027-02-10 12:00:00",
    "Transit_2028-07-20":     "2028-07-20 12:00:00",
    "Transit_2028-11-05":     "2028-11-05 12:00:00",
}

# ===== CHROME AGENT DATA (extracted from chrome.json.txt) =====
CHROME_D1 = {
    "Sector_ETFs_Conception": {
        "Sun": "Sagittarius 00° 42'", "Moon": "Scorpio 05° 45'", "Mars": "Virgo 16° 42'",
        "Mercury": "Scorpio 09° 38'", "Jupiter": "Aquarius 26° 10'", "Venus": "Sagittarius 12° 22'",
        "Saturn": "Aries 03° 03' (R)", "Rahu": "Leo 01° 21'", "Ketu": "Aquarius 01° 21'",
        "Ascendant": "Aquarius 29° 26'"
    },
    "XLRE_Conception": {
        "Sun": "Virgo 19° 00'", "Moon": "Cancer 09° 46'", "Mars": "Leo 13° 08'",
        "Mercury": "Virgo 07° 36' (R)", "Jupiter": "Leo 17° 54'", "Venus": "Leo 04° 16'",
        "Saturn": "Scorpio 07° 25'", "Rahu": "Virgo 06° 05'", "Ketu": "Pisces 06° 05'",
        "Ascendant": "Scorpio 17° 51'"
    },
    "XLC_Conception": {
        "Sun": "Gemini 03° 16'", "Moon": "Leo 10° 13'", "Mars": "Capricorn 14° 44'",
        "Mercury": "Gemini 17° 42'", "Jupiter": "Libra 19° 58' (R)", "Venus": "Cancer 11° 25'",
        "Saturn": "Sagittarius 12° 22' (R)", "Rahu": "Cancer 13° 50'", "Ketu": "Capricorn 13° 50'",
        "Ascendant": "Leo 22° 16'"
    },
    "Transit_2024-11-05": {
        "Sun": "Libra 19° 34'", "Moon": "Sagittarius 06° 41'", "Mars": "Cancer 06° 17'",
        "Mercury": "Scorpio 09° 47'", "Jupiter": "Taurus 25° 50' (R)", "Venus": "Scorpio 28° 33'",
        "Saturn": "Aquarius 18° 33' (R)", "Rahu": "Pisces 10° 16'", "Ketu": "Virgo 10° 16'"
    },
    "Transit_2025-02-10": {
        "Sun": "Capricorn 28° 00'", "Moon": "Cancer 05° 46'", "Mars": "Gemini 23° 56' (R)",
        "Mercury": "Capricorn 28° 56'", "Jupiter": "Taurus 17° 05'", "Venus": "Pisces 10° 07'",
        "Saturn": "Aquarius 24° 17'", "Rahu": "Pisces 05° 07'", "Ketu": "Virgo 05° 07'"
    },
}

print("=" * 90)
print("MASTER COMPARISON: CHROME AGENT vs PYTHON BACKEND (Swiss Ephemeris)")
print("=" * 90)

for label, dt_str in TEST_CASES.items():
    print(f"\n{'━'*90}")
    print(f"  DATE: {label} ({dt_str})")
    print(f"{'━'*90}")
    backend = calc_full(dt_str)
    
    if label in CHROME_D1:
        chrome = CHROME_D1[label]
        print(f"  {'Planet':<12} {'CHROME AGENT':>35} {'BACKEND (Swiss Eph)':>35}  MATCH?")
        print(f"  {'-'*85}")
        for planet in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu","Ascendant"]:
            if planet not in chrome:
                continue
            chrome_val = chrome[planet]
            backend_val = backend["D1"][planet]
            # Compare just sign and degree (strip seconds for tolerance)
            chrome_sign = chrome_val.split()[0]
            backend_sign = backend_val.split()[0]
            chrome_deg = chrome_val.split()[1] if len(chrome_val.split()) > 1 else ""
            backend_deg = backend_val.split()[1] if len(backend_val.split()) > 1 else ""
            match = "✅" if chrome_sign == backend_sign and chrome_deg[:4] == backend_deg[:4] else "❌ MISMATCH"
            print(f"  {planet:<12} {chrome_val:>35} {backend_val:>35}  {match}")
    else:
        print("  (No Chrome comparison data for this date - Backend only)")
        print(f"  {'Planet':<12} {'BACKEND (Swiss Eph)':>35}")
        print(f"  {'-'*55}")
        for planet in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu","Ascendant"]:
            print(f"  {planet:<12} {backend['D1'][planet]:>35}")
    
    # Print D9 Backend
    print(f"\n  D9 (Navamsa) - Backend: {backend['D9']}")
    print(f"  D10 (Dasamsa) - Backend: {backend['D10']}")
    print(f"  Moon Nakshatra - Backend: {backend['Moon_Nakshatra']}")
