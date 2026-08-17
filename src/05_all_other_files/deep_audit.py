import json
import swisseph as swe
from datetime import datetime
import pytz
import sys
sys.stdout.reconfigure(encoding='utf-8')

swe.set_ephe_path(None)
swe.set_sid_mode(swe.SIDM_LAHIRI)

PLANET_IDS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE
}
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

ASHTAKVARGA_RULES = {
    "Sun":     {"Sun":[1,2,4,7,8,9,10,11],"Moon":[3,6,10,11],"Mars":[1,2,4,7,8,9,10,11],
                "Mercury":[3,5,6,9,10,11,12],"Jupiter":[5,6,9,11],"Venus":[6,7,12],
                "Saturn":[1,2,4,7,8,9,10,11],"Ascendant":[3,4,6,10,11,12]},
    "Moon":    {"Sun":[3,6,7,8,10,11],"Moon":[1,3,6,7,10,11],"Mars":[2,3,5,6,9,10,11],
                "Mercury":[1,3,4,5,7,8,10,11],"Jupiter":[1,4,7,8,10,11,12],"Venus":[3,4,5,7,9,10,11],
                "Saturn":[3,5,6,11],"Ascendant":[3,6,10,11]},
    "Mars":    {"Sun":[3,5,6,10,11],"Moon":[3,6,11],"Mars":[1,2,4,7,8,10,11],
                "Mercury":[3,5,6,11],"Jupiter":[6,10,11,12],"Venus":[6,8,11,12],
                "Saturn":[1,4,7,8,9,10,11],"Ascendant":[1,3,6,10,11]},
    "Mercury": {"Sun":[5,6,9,11,12],"Moon":[2,4,6,8,10,11],"Mars":[1,2,4,7,8,9,10,11],
                "Mercury":[1,3,5,6,9,10,11,12],"Jupiter":[6,8,11,12],"Venus":[1,2,3,4,5,8,9,11],
                "Saturn":[1,2,4,7,8,9,10,11],"Ascendant":[1,2,4,6,8,10,11]},
    "Jupiter": {"Sun":[1,2,3,4,7,8,9,10,11],"Moon":[2,5,7,9,11],"Mars":[1,2,4,7,8,10,11],
                "Mercury":[1,2,4,5,6,9,10,11],"Jupiter":[1,2,3,4,7,8,10,11],"Venus":[2,5,6,9,10,11],
                "Saturn":[3,5,6,12],"Ascendant":[1,2,4,5,6,9,10,11]},
    "Venus":   {"Sun":[8,11,12],"Moon":[1,2,3,4,5,8,9,11,12],"Mars":[3,5,6,9,11,12],
                "Mercury":[3,5,6,9,11],"Jupiter":[5,8,9,10,11],"Venus":[1,2,3,4,5,8,9,10,11],
                "Saturn":[3,4,5,8,9,10,11],"Ascendant":[1,2,3,4,5,8,9,11]},
    "Saturn":  {"Sun":[1,2,4,7,8,10,11],"Moon":[3,6,11],"Mars":[3,5,6,10,11],
                "Mercury":[6,8,9,10,11,12],"Jupiter":[5,6,11,12],"Venus":[6,11,12],
                "Saturn":[3,5,6,11],"Ascendant":[1,3,4,6,10,11]}
}

def calc_full(dt_string):
    ny_tz = pytz.timezone('America/New_York')
    dt_naive = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
    dt_ny = ny_tz.localize(dt_naive)
    dt_utc = dt_ny.astimezone(pytz.utc)
    utc_hour = dt_utc.hour + (dt_utc.minute / 60.0) + (dt_utc.second / 3600.0)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, utc_hour)
    flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH

    pos_raw = {}
    d1_text = {}
    retro_flags = {}

    for p_name, p_id in PLANET_IDS.items():
        res = swe.calc_ut(jd, p_id, flags)
        lon = res[0][0]
        spd = res[0][3]
        pos_raw[p_name] = lon
        retro_flags[p_name] = spd < 0
        sign = SIGNS[int(lon/30)%12]
        deg = int(lon%30)
        m = int((lon%30 - deg)*60)
        s = int(((lon%30 - deg)*60 - m)*60)
        d1_text[p_name] = f"{sign} {deg:02d}° {m:02d}' {s:02d}\"{'(R)' if spd<0 else ''}"

    ketu_lon = (pos_raw["Rahu"] + 180.0) % 360.0
    pos_raw["Ketu"] = ketu_lon
    sign = SIGNS[int(ketu_lon/30)%12]
    deg = int(ketu_lon%30); m = int((ketu_lon%30-deg)*60); s = int(((ketu_lon%30-deg)*60-m)*60)
    d1_text["Ketu"] = f"{sign} {deg:02d}° {m:02d}' {s:02d}\""

    houses, ascmc = swe.houses_ex(jd, 40.7128, -74.0060, b'W', flags)
    asc_lon = ascmc[0]
    pos_raw["Ascendant"] = asc_lon
    sign = SIGNS[int(asc_lon/30)%12]; deg = int(asc_lon%30); m = int((asc_lon%30-deg)*60); s = int(((asc_lon%30-deg)*60-m)*60)
    d1_text["Ascendant"] = f"{sign} {deg:02d}° {m:02d}' {s:02d}\""

    # D9
    d9 = {p: SIGNS[int(lon / (10.0/3.0)) % 12] for p, lon in pos_raw.items()}

    # D10
    d10 = {}
    for p, lon in pos_raw.items():
        si = int(lon/30); pi = int((lon%30)/3.0)
        d10[p] = SIGNS[(si+pi)%12] if si%2==0 else SIGNS[(si+8+pi)%12]

    # Ashtakvarga - Bhinnashtakavarga per planet
    bhinna = {p: [0]*12 for p in ASHTAKVARGA_RULES.keys()}
    sign_idx = {p: int(lon/30)%12 for p,lon in pos_raw.items()}

    for transiting_planet, rules in ASHTAKVARGA_RULES.items():
        for contributor, rel_positions in rules.items():
            s = sign_idx[contributor]
            for r in rel_positions:
                bhinna[transiting_planet][(s + r - 1) % 12] += 1

    # Sarvashtakavarga (total per house)
    sarva = [0]*12
    for p_bindus in bhinna.values():
        for i in range(12):
            sarva[i] += p_bindus[i]

    # House labeling: House 1 = Ascendant sign
    asc_sign_idx = int(asc_lon/30)%12
    sarva_labeled = {}
    bhinna_labeled = {p: {} for p in bhinna.keys()}
    for i in range(12):
        house_num = i+1
        sign_name = SIGNS[(asc_sign_idx+i)%12]
        sarva_labeled[f"H{house_num}_{sign_name[:2]}"] = sarva[(asc_sign_idx+i)%12]
        for p in bhinna.keys():
            bhinna_labeled[p][f"H{house_num}_{sign_name[:2]}"] = bhinna[p][(asc_sign_idx+i)%12]

    return {"D1": d1_text, "D9": d9, "D10": d10, "Sarva": sarva_labeled, "Sarva_raw": sarva, "Bhinna": bhinna_labeled, "Asc_sign_idx": asc_sign_idx, "pos_raw": pos_raw}


# ===========================
# CHROME AGENT DATA (from chrome.json.txt)
# ===========================
CHROME_DATA = {
    "Sector_ETFs_Conception_1998-12-16": {
        "dt": "1998-12-16 12:00:00",
        "chrome_d9": {"Asc":"Aries","Sun":"Aries","Moon":"Leo","Mars":"Capricorn","Mercury":"Sagittarius","Jupiter":"Taurus","Venus":"Cancer","Saturn":"Aries","Rahu":"Aries","Ketu":"Libra"},
        "chrome_d10": {"Asc":"Scorpio","Sun":"Sagittarius","Moon":"Leo","Mars":"Libra","Mercury":"Libra","Jupiter":"Libra","Venus":"Aries","Saturn":"Taurus","Rahu":"Virgo","Ketu":"Aquarius"},
        "chrome_sav": {"H1":26,"H2":23,"H3":30,"H4":23,"H5":25,"H6":36,"H7":24,"H8":35,"H9":29,"H10":27,"H11":31,"H12":28}
    },
    "Sector_ETFs_Trading_1998-12-22": {
        "dt": "1998-12-22 09:30:00",
        "chrome_d9": {"Asc":"Aries","Sun":"Taurus","Moon":"Taurus","Mars":"Taurus","Mercury":"Sagittarius","Jupiter":"Taurus","Venus":"Leo","Saturn":"Aries","Rahu":"Aries","Ketu":"Libra"},
        "chrome_d10": {"Asc":"Sagittarius","Sun":"Aquarius","Moon":"Pisces","Mars":"Scorpio","Mercury":"Sagittarius","Jupiter":"Libra","Venus":"Gemini","Saturn":"Aries","Rahu":"Leo","Ketu":"Aquarius"},
        "chrome_sav": {"H1":29,"H2":25,"H3":28,"H4":27,"H5":20,"H6":32,"H7":31,"H8":24,"H9":30,"H10":35,"H11":33,"H12":23}
    },
    "XLRE_Conception_2015-10-06": {
        "dt": "2015-10-06 12:00:00",
        "chrome_d9": {"Asc":"Gemini","Sun":"Pisces","Moon":"Scorpio","Mars":"Taurus","Mercury":"Gemini","Jupiter":"Scorpio","Venus":"Cancer","Saturn":"Virgo","Rahu":"Gemini","Ketu":"Sagittarius"},
        "chrome_d10": {"Asc":"Sagittarius","Sun":"Scorpio","Moon":"Taurus","Mars":"Sagittarius","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Virgo","Rahu":"Cancer","Ketu":"Aquarius"},
        "chrome_sav": {"H1":27,"H2":25,"H3":30,"H4":28,"H5":24,"H6":29,"H7":32,"H8":37,"H9":31,"H10":26,"H11":33,"H12":15}
    },
    "XLRE_Trading_2015-10-08": {
        "dt": "2015-10-08 09:30:00",
        "chrome_d9": {"Lagna":"Pisces","Sun":"Leo","Moon":"Aquarius","Mars":"Cancer","Mercury":"Aquarius","Jupiter":"Sagittarius","Venus":"Taurus","Saturn":"Sagittarius","Rahu":"Capricorn","Ketu":"Virgo"},
        "chrome_d10": {"Lagna":"Aries","Sun":"Sagittarius","Moon":"Leo","Mars":"Capricorn","Mercury":"Cancer","Jupiter":"Aquarius","Venus":"Pisces","Saturn":"Libra","Rahu":"Gemini","Ketu":"Capricorn"},
        "chrome_sav": {"H1":23,"H2":29,"H3":43,"H4":34,"H5":26,"H6":25,"H7":22,"H8":25,"H9":24,"H10":33,"H11":25,"H12":28}
    },
    "XLC_Conception_2018-06-18": {
        "dt": "2018-06-18 12:00:00",
        "chrome_d9": {"Lagna":"Capricorn","Sun":"Gemini","Moon":"Cancer","Mars":"Aries","Mercury":"Aquarius","Jupiter":"Aquarius","Venus":"Virgo","Saturn":"Sagittarius","Rahu":"Taurus","Ketu":"Scorpio"},
        "chrome_d10": {"Lagna":"Aries","Sun":"Cancer","Moon":"Scorpio","Mars":"Capricorn","Mercury":"Gemini","Jupiter":"Aries","Venus":"Gemini","Saturn":"Aries","Rahu":"Cancer","Ketu":"Capricorn"},
        "chrome_sav": {"H1":31,"H2":30,"H3":31,"H4":20,"H5":33,"H6":26,"H7":35,"H8":29,"H9":19,"H10":28,"H11":26,"H12":29}
    },
    "SMH_Conception_2000-12-18": {
        "dt": "2000-12-18 12:00:00",
        "chrome_d9": {"Asc":"Leo","Sun":"Pisces","Moon":"Pisces","Mars":"Scorpio","Mercury":"Virgo","Jupiter":"Virgo","Venus":"Aries","Saturn":"Capricorn","Rahu":"Pisces","Ketu":"Scorpio"},
        "chrome_d10": {"Asc":"Sagittarius","Sun":"Capricorn","Moon":"Leo","Mars":"Scorpio","Mercury":"Aries","Jupiter":"Aries","Venus":"Pisces","Saturn":"Aquarius","Rahu":"Capricorn","Ketu":"Leo"},
        "chrome_sav": {"H1":25,"H2":24,"H3":25,"H4":32,"H5":31,"H6":28,"H7":29,"H8":28,"H9":26,"H10":29,"H11":25,"H12":35}
    },
    "XME_Conception_2006-06-19": {
        "dt": "2006-06-19 12:00:00",
        "chrome_d9": {"Asc":"Libra","Sun":"Sagittarius","Moon":"Sagittarius","Mars":"Scorpio","Mercury":"Libra","Jupiter":"Libra","Venus":"Libra","Saturn":"Scorpio","Rahu":"Cancer","Ketu":"Aries"},
        "chrome_d10": {"Asc":"Pisces","Sun":"Cancer","Moon":"Aries","Mars":"Leo","Mercury":"Pisces","Jupiter":"Taurus","Venus":"Capricorn","Saturn":"Cancer","Rahu":"Capricorn","Ketu":"Cancer"},
        "chrome_sav": {"H1":34,"H2":35,"H3":23,"H4":21,"H5":35,"H6":25,"H7":29,"H8":26,"H9":20,"H10":33,"H11":24,"H12":32}
    },
}

print("=" * 110)
print("DEEP AUDIT: D9 (NAVAMSA) + D10 (DASAMSA) + ASHTAKVARGA vs CHROME AGENT")
print("=" * 110)

total_mismatches = 0
total_checks = 0

for case_label, case_data in CHROME_DATA.items():
    dt_str = case_data["dt"]
    backend = calc_full(dt_str)
    
    print(f"\n{'━'*110}")
    print(f"  CASE: {case_label}  [{dt_str}]")
    print(f"{'━'*110}")
    
    # --- D9 Comparison ---
    print(f"\n  [D9 NAVAMSA]")
    print(f"  {'Planet':<12} {'CHROME':>18} {'BACKEND':>18}  STATUS")
    print(f"  {'-'*60}")
    chrome_d9 = case_data["chrome_d9"]
    for planet in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu","Ascendant"]:
        chrome_key = planet if planet in chrome_d9 else ("Asc" if "Asc" in chrome_d9 else "Lagna")
        if planet == "Ascendant":
            chrome_val = chrome_d9.get("Asc", chrome_d9.get("Lagna", chrome_d9.get("Ascendant","N/A")))
        else:
            chrome_val = chrome_d9.get(planet, "N/A")
        backend_val = backend["D9"].get(planet, "N/A")
        match = "✅" if chrome_val == backend_val else "❌ MISMATCH"
        if match == "❌ MISMATCH": total_mismatches += 1
        total_checks += 1
        print(f"  {planet:<12} {chrome_val:>18} {backend_val:>18}  {match}")
    
    # --- D10 Comparison ---
    print(f"\n  [D10 DASAMSA]")
    print(f"  {'Planet':<12} {'CHROME':>18} {'BACKEND':>18}  STATUS")
    print(f"  {'-'*60}")
    chrome_d10 = case_data["chrome_d10"]
    for planet in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu","Ascendant"]:
        if planet == "Ascendant":
            chrome_val = chrome_d10.get("Asc", chrome_d10.get("Lagna", chrome_d10.get("Ascendant","N/A")))
        else:
            chrome_val = chrome_d10.get(planet, "N/A")
        backend_val = backend["D10"].get(planet, "N/A")
        match = "✅" if chrome_val == backend_val else "❌ MISMATCH"
        if match == "❌ MISMATCH": total_mismatches += 1
        total_checks += 1
        print(f"  {planet:<12} {chrome_val:>18} {backend_val:>18}  {match}")
    
    # --- Ashtakvarga SAV Comparison ---
    print(f"\n  [SARVASHTAKVARGA - Total Points Per House]")
    print(f"  {'House':<10} {'CHROME SAV':>12} {'BACKEND SAV':>12}  STATUS")
    print(f"  {'-'*48}")
    chrome_sav = case_data["chrome_sav"]
    asc_idx = backend["Asc_sign_idx"]
    
    for i, (h_key, chrome_val) in enumerate(chrome_sav.items()):
        # Backend houses indexed from Ascendant sign
        sign_for_house = SIGNS[(asc_idx + i) % 12]
        backend_val = backend["Sarva_raw"][(asc_idx + i) % 12]
        match = "✅" if chrome_val == backend_val else f"❌ DIFF ({chrome_val - backend_val:+d})"
        if "DIFF" in match: total_mismatches += 1
        total_checks += 1
        print(f"  H{i+1:<9} {chrome_val:>12} {backend_val:>12}  {match}")

print(f"\n{'='*110}")
print(f"  FINAL AUDIT SUMMARY")
print(f"  Total Checks: {total_checks}")
print(f"  Mismatches:   {total_mismatches}")
print(f"  Match Rate:   {((total_checks - total_mismatches)/total_checks)*100:.1f}%")
print(f"{'='*110}")


# CRITICAL BUG FIX #17: Ensure swisseph is closed
import atexit
atexit.register(swe.close)
