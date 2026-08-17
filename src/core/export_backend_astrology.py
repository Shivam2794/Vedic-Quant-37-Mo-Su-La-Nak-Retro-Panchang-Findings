import json
import swisseph as swe
from datetime import datetime
import pytz

swe.set_ephe_path(None)
swe.set_sid_mode(swe.SIDM_LAHIRI)

PLANET_IDS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE, "Ketu": swe.MEAN_NODE
}

ASHTAKVARGA_RULES = {
    "Sun": {"Sun": [1,2,4,7,8,9,10,11], "Moon": [3,6,10,11], "Mars": [1,2,4,7,8,9,10,11],
            "Mercury": [3,5,6,9,10,11,12], "Jupiter": [5,6,9,11], "Venus": [6,7,12],
            "Saturn": [1,2,4,7,8,9,10,11], "Ascendant": [3,4,6,10,11,12]},
    "Moon": {"Sun": [3,6,7,8,10,11], "Moon": [1,3,6,7,10,11], "Mars": [2,3,5,6,9,10,11],
             "Mercury": [1,3,4,5,7,8,10,11], "Jupiter": [1,4,7,8,10,11,12], "Venus": [3,4,5,7,9,10,11],
             "Saturn": [3,5,6,11], "Ascendant": [3,6,10,11]},
    "Mars": {"Sun": [3,5,6,10,11], "Moon": [3,6,11], "Mars": [1,2,4,7,8,10,11],
             "Mercury": [3,5,6,11], "Jupiter": [6,10,11,12], "Venus": [6,8,11,12],
             "Saturn": [1,4,7,8,9,10,11], "Ascendant": [1,3,6,10,11]},
    "Mercury": {"Sun": [5,6,9,11,12], "Moon": [2,4,6,8,10,11], "Mars": [1,2,4,7,8,9,10,11],
                "Mercury": [1,3,5,6,9,10,11,12], "Jupiter": [6,8,11,12], "Venus": [1,2,3,4,5,8,9,11],
                "Saturn": [1,2,4,7,8,9,10,11], "Ascendant": [1,2,4,6,8,10,11]},
    "Jupiter": {"Sun": [1,2,3,4,7,8,9,10,11], "Moon": [2,5,7,9,11], "Mars": [1,2,4,7,8,10,11],
                "Mercury": [1,2,4,5,6,9,10,11], "Jupiter": [1,2,3,4,7,8,10,11], "Venus": [2,5,6,9,10,11],
                "Saturn": [3,5,6,12], "Ascendant": [1,2,4,5,6,9,10,11]},
    "Venus": {"Sun": [8,11,12], "Moon": [1,2,3,4,5,8,9,11,12], "Mars": [3,5,6,9,11,12],
              "Mercury": [3,5,6,9,11], "Jupiter": [5,8,9,10,11], "Venus": [1,2,3,4,5,8,9,10,11],
              "Saturn": [3,4,5,8,9,10,11], "Ascendant": [1,2,3,4,5,8,9,11]},
    "Saturn": {"Sun": [1,2,4,7,8,10,11], "Moon": [3,6,11], "Mars": [3,5,6,10,11],
               "Mercury": [6,8,9,10,11,12], "Jupiter": [5,6,11,12], "Venus": [6,11,12],
               "Saturn": [3,5,6,11], "Ascendant": [1,3,4,6,10,11]}
}
DASHA_RULERS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]
TOTAL_YEARS = 120.0

def calc_astrology(dt_string):
    ny_tz = pytz.timezone('America/New_York')
    dt_naive = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
    dt_ny = ny_tz.localize(dt_naive)
    dt_utc = dt_ny.astimezone(pytz.utc)
    utc_hour = dt_utc.hour + (dt_utc.minute / 60.0) + (dt_utc.second / 3600.0)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, utc_hour)
    
    pos, signs, d9, d10 = {}, {}, {}, {}
    flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH
    for p_name, p_id in PLANET_IDS.items():
        if p_name == "Ketu":
            val = (pos["Rahu"] + 180.0) % 360.0
        else:
            val = swe.calc_ut(jd, p_id, flags)[0][0]
        pos[p_name] = val
        signs[p_name] = int(val / 30) % 12
        d9[p_name] = int(val / (10.0 / 3.0)) % 12
        sign_idx = int(val / 30)
        part_idx = int((val % 30) / 3.0)
        if sign_idx % 2 == 0:
            d10[p_name] = (sign_idx + part_idx) % 12
        else:
            d10[p_name] = (sign_idx + 8 + part_idx) % 12
            
    houses, ascmc = swe.houses_ex(jd, 40.7128, -74.0060, b'W', flags)
    pos["Ascendant"] = ascmc[0]
    signs["Ascendant"] = int(ascmc[0] / 30) % 12
    d9["Ascendant"] = int(ascmc[0] / (10.0 / 3.0)) % 12
    sign_idx = int(ascmc[0] / 30)
    part_idx = int((ascmc[0] % 30) / 3.0)
    d10["Ascendant"] = (sign_idx + part_idx) % 12 if sign_idx % 2 == 0 else (sign_idx + 8 + part_idx) % 12
    
    bindus = {p: [0]*12 for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]}
    for transiting, rules in ASHTAKVARGA_RULES.items():
        for contrib, rel_signs in rules.items():
            s = signs[contrib]
            for r in rel_signs:
                bindus[transiting][(s + r - 1) % 12] += 1
                
    total_sarvashtak = [0]*12
    for b in bindus.values():
        for i in range(12):
            total_sarvashtak[i] += b[i]
            
    moon_lon = pos["Moon"]
    n_size = 360.0 / 27.0
    n_idx = int(moon_lon / n_size)
    start_idx = n_idx % 9
    
    maha_lord = DASHA_RULERS[start_idx]
    antar_lord = DASHA_RULERS[start_idx]
    prat_lord = DASHA_RULERS[start_idx]
    
    return {
        "D1_Signs": signs,
        "D9_Navamsa_Signs": d9,
        "D10_Dasamsa_Signs": d10,
        "Ashtakvarga_Total_Per_House": total_sarvashtak,
        "Dasha_At_Birth": f"{maha_lord}-{antar_lord}-{prat_lord}"
    }

if __name__ == "__main__":
    db_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\asset_birth_database.json"
    with open(db_path, "r") as f:
        birth_db = json.load(f)
    
    results = {}
    for ticker, dates in birth_db.items():
        results[ticker] = {
            "Conception": calc_astrology(dates["conception"]),
            "Trading": calc_astrology(dates["trading"])
        }
    
    with open("backend_astro_verification.json", "w") as f:
        json.dump(results, f, indent=4)
    print("Done!")


# CRITICAL BUG FIX #17: Ensure swisseph is closed
import atexit
atexit.register(swe.close)
