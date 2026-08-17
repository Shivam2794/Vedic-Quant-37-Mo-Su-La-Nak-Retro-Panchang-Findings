"""
FINAL FORMULA FIX + FULL COMPARISON
After formula investigation:

D9 ISSUE: Our navamsa formula uses element-based starting signs but is STILL failing
          for many planets. The issue is the degree boundary at 30° navamsa boundaries.
          Need to investigate exact navamsa number calculation.

D10 ISSUE: 6 failures out of 24. Let's trace each failure precisely.

SAV ISSUE: Inconsistent house labeling by Chrome agent. Must compute both absolute
           and Ascendant-relative and see which matches Chrome.
"""
import sys, swisseph as swe
from datetime import datetime
import pytz
sys.stdout.reconfigure(encoding='utf-8')

swe.set_ephe_path(None)
swe.set_sid_mode(swe.SIDM_LAHIRI)

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

# D9: Element-based start
D9_STARTS = {0:0,4:0,8:0,  1:9,5:9,9:9,  2:6,6:6,10:6,  3:3,7:3,11:3}

def navamsa_correct(lon):
    """Correct D9: each navamsa = 3°20' = 10/3 degrees"""
    sign_idx = int(lon / 30) % 12
    deg_in_sign = lon % 30
    nav_num = int(deg_in_sign * 9 / 30)  # 0..8
    start = D9_STARTS[sign_idx]
    return SIGNS[(start + nav_num) % 12]

def dasamsa_correct(lon):
    """Correct D10: odd Sanskrit sign = index 0,2,4,6,8,10"""
    sign_idx = int(lon / 30) % 12
    deg_in_sign = lon % 30
    part = int(deg_in_sign / 3.0)
    if sign_idx % 2 == 0:  # odd Sanskrit = Aries,Gem,Leo,Lib,Sag,Aq
        return SIGNS[(sign_idx + part) % 12]
    else:  # even Sanskrit = Tau,Can,Vir,Sco,Cap,Pis
        return SIGNS[(sign_idx + 8 + part) % 12]

PLANET_IDS = {"Sun":swe.SUN,"Moon":swe.MOON,"Mars":swe.MARS,"Mercury":swe.MERCURY,
              "Jupiter":swe.JUPITER,"Venus":swe.VENUS,"Saturn":swe.SATURN,"Rahu":swe.MEAN_NODE}

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

def calc_chart(dt_string):
    ny_tz = pytz.timezone('America/New_York')
    dt_naive = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
    dt_ny = ny_tz.localize(dt_naive)
    dt_utc = dt_ny.astimezone(pytz.utc)
    utc_hour = dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, utc_hour)
    flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH

    pos_raw = {}
    d1_text = {}
    for p, pid in PLANET_IDS.items():
        res = swe.calc_ut(jd, pid, flags)
        lon = res[0][0]; spd = res[0][3]
        pos_raw[p] = lon
        sign = SIGNS[int(lon/30)%12]; d=int(lon%30); m=int((lon%30-d)*60); s=int(((lon%30-d)*60-m)*60)
        d1_text[p] = f"{sign} {d:02d}°{m:02d}'{s:02d}\"{'(R)' if spd<0 else ''}"

    pos_raw["Ketu"] = (pos_raw["Rahu"] + 180.0) % 360.0
    klon = pos_raw["Ketu"]; sign=SIGNS[int(klon/30)%12]; d=int(klon%30); m=int((klon%30-d)*60); s=int(((klon%30-d)*60-m)*60)
    d1_text["Ketu"] = f"{sign} {d:02d}°{m:02d}'{s:02d}\""

    houses, ascmc = swe.houses_ex(jd, 40.7128, -74.0060, b'W', flags)
    asc_lon = ascmc[0]
    pos_raw["Ascendant"] = asc_lon
    asc_idx = int(asc_lon/30)%12
    sign=SIGNS[asc_idx]; d=int(asc_lon%30); m=int((asc_lon%30-d)*60); s=int(((asc_lon%30-d)*60-m)*60)
    d1_text["Ascendant"] = f"{sign} {d:02d}°{m:02d}'{s:02d}\""

    # D9 + D10
    d9 = {p: navamsa_correct(lon) for p, lon in pos_raw.items()}
    d10 = {p: dasamsa_correct(lon) for p, lon in pos_raw.items()}

    # Ashtakvarga - compute raw per absolute sign index
    all_planets_for_avk = {"Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Ascendant"}
    sign_idx = {p: int(lon/30)%12 for p,lon in pos_raw.items()}

    bhinna = {p: [0]*12 for p in ASHTAKVARGA_RULES.keys()}
    for tp, rules in ASHTAKVARGA_RULES.items():
        for contributor, rel_positions in rules.items():
            s = sign_idx[contributor]
            for r in rel_positions:
                bhinna[tp][(s + r - 1) % 12] += 1

    sarva_abs = [0]*12  # indexed by absolute zodiac (0=Aries)
    for p_bindus in bhinna.values():
        for i in range(12): sarva_abs[i] += p_bindus[i]

    # Also produce Ascendant-relative version
    sarva_from_asc = {}
    for i in range(12):
        sarva_from_asc[SIGNS[(asc_idx+i)%12]] = sarva_abs[(asc_idx+i)%12]

    sarva_absolute = {SIGNS[i]: sarva_abs[i] for i in range(12)}

    return {"D1": d1_text, "D9": d9, "D10": d10, 
            "SAV_abs": sarva_absolute, "SAV_from_asc": sarva_from_asc,
            "asc_sign": SIGNS[asc_idx]}

# ============================================================
# ALL CHROME CASES WITH EXACT DATA
# ============================================================
CHROME_CASES = {
    "XLK_Conception_1998-12-16_12:00": {
        "dt": "1998-12-16 12:00:00",
        "chrome_d9":  {"Ascendant":"Aries","Sun":"Aries","Moon":"Leo","Mars":"Capricorn","Mercury":"Sagittarius","Jupiter":"Taurus","Venus":"Cancer","Saturn":"Aries","Rahu":"Aries","Ketu":"Libra"},
        "chrome_d10": {"Ascendant":"Scorpio","Sun":"Sagittarius","Moon":"Leo","Mars":"Libra","Mercury":"Libra","Jupiter":"Libra","Venus":"Aries","Saturn":"Taurus","Rahu":"Virgo","Ketu":"Aquarius"},
        "chrome_sav_labeled": {"Aquarius":26,"Pisces":23,"Aries":30,"Taurus":23,"Gemini":25,"Cancer":36,"Leo":24,"Virgo":35,"Libra":29,"Scorpio":27,"Sagittarius":31,"Capricorn":28}
    },
    "XLK_Trading_1998-12-22_09:30": {
        "dt": "1998-12-22 09:30:00",
        "chrome_d9":  {"Ascendant":"Aries","Sun":"Taurus","Moon":"Taurus","Mars":"Taurus","Mercury":"Sagittarius","Jupiter":"Taurus","Venus":"Leo","Saturn":"Aries","Rahu":"Aries","Ketu":"Libra"},
        "chrome_d10": {"Ascendant":"Sagittarius","Sun":"Aquarius","Moon":"Pisces","Mars":"Scorpio","Mercury":"Sagittarius","Jupiter":"Libra","Venus":"Gemini","Saturn":"Aries","Rahu":"Leo","Ketu":"Aquarius"},
        "chrome_sav_labeled": {"Capricorn":29,"Aquarius":25,"Pisces":28,"Aries":27,"Taurus":20,"Gemini":32,"Cancer":31,"Leo":24,"Virgo":30,"Libra":35,"Scorpio":33,"Sagittarius":23}
    },
    "XLRE_Conception_2015-10-06_12:00": {
        "dt": "2015-10-06 12:00:00",
        "chrome_d9":  {"Ascendant":"Gemini","Sun":"Pisces","Moon":"Scorpio","Mars":"Taurus","Mercury":"Gemini","Jupiter":"Scorpio","Venus":"Cancer","Saturn":"Virgo","Rahu":"Gemini","Ketu":"Sagittarius"},
        "chrome_d10": {"Ascendant":"Sagittarius","Sun":"Scorpio","Moon":"Taurus","Mars":"Sagittarius","Mercury":"Pisces","Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Virgo","Rahu":"Cancer","Ketu":"Aquarius"},
        "chrome_sav_labeled": {"Scorpio":27,"Sagittarius":25,"Capricorn":30,"Aquarius":28,"Pisces":24,"Aries":29,"Taurus":32,"Gemini":37,"Cancer":31,"Leo":26,"Virgo":33,"Libra":15}
    },
    "XLRE_Trading_2015-10-08_09:30": {
        "dt": "2015-10-08 09:30:00",
        "chrome_d9":  {"Ascendant":"Pisces","Sun":"Leo","Moon":"Aquarius","Mars":"Cancer","Mercury":"Aquarius","Jupiter":"Sagittarius","Venus":"Taurus","Saturn":"Sagittarius","Rahu":"Capricorn","Ketu":"Virgo"},
        "chrome_d10": {"Ascendant":"Aries","Sun":"Sagittarius","Moon":"Leo","Mars":"Capricorn","Mercury":"Cancer","Jupiter":"Aquarius","Venus":"Pisces","Saturn":"Libra","Rahu":"Gemini","Ketu":"Capricorn"},
        "chrome_sav_labeled": {"Aries":23,"Taurus":29,"Gemini":43,"Cancer":34,"Leo":26,"Virgo":25,"Libra":22,"Scorpio":25,"Sagittarius":24,"Capricorn":33,"Aquarius":25,"Pisces":28}
    },
    "XLC_Conception_2018-06-18_12:00": {
        "dt": "2018-06-18 12:00:00",
        "chrome_d9":  {"Ascendant":"Capricorn","Sun":"Gemini","Moon":"Cancer","Mars":"Aries","Mercury":"Aquarius","Jupiter":"Aquarius","Venus":"Virgo","Saturn":"Sagittarius","Rahu":"Taurus","Ketu":"Scorpio"},
        "chrome_d10": {"Ascendant":"Aries","Sun":"Cancer","Moon":"Scorpio","Mars":"Capricorn","Mercury":"Gemini","Jupiter":"Aries","Venus":"Gemini","Saturn":"Aries","Rahu":"Cancer","Ketu":"Capricorn"},
        "chrome_sav_labeled": {"Aries":31,"Taurus":30,"Gemini":31,"Cancer":20,"Leo":33,"Virgo":26,"Libra":35,"Scorpio":29,"Sagittarius":19,"Capricorn":28,"Aquarius":26,"Pisces":29}
    },
    "XLC_Trading_2018-06-19_09:30": {
        "dt": "2018-06-19 09:30:00",
        "chrome_d9":  {"Ascendant":"Sagittarius","Sun":"Leo","Moon":"Scorpio","Mars":"Taurus","Mercury":"Aries","Jupiter":"Aquarius","Venus":"Scorpio","Saturn":"Cancer","Rahu":"Leo","Ketu":"Taurus"},
        "chrome_d10": {"Ascendant":"Libra","Sun":"Cancer","Moon":"Pisces","Mars":"Capricorn","Mercury":"Sagittarius","Jupiter":"Aries","Venus":"Virgo","Saturn":"Aries","Rahu":"Cancer","Ketu":"Capricorn"},
        "chrome_sav_labeled": {"Aries":35,"Taurus":31,"Gemini":25,"Cancer":24,"Leo":31,"Virgo":28,"Libra":35,"Scorpio":26,"Sagittarius":23,"Capricorn":23,"Aquarius":27,"Pisces":29}
    },
    "SMH_Conception_2000-12-18_12:00": {
        "dt": "2000-12-18 12:00:00",
        "chrome_d9":  {"Ascendant":"Leo","Sun":"Pisces","Moon":"Pisces","Mars":"Scorpio","Mercury":"Virgo","Jupiter":"Virgo","Venus":"Aries","Saturn":"Capricorn","Rahu":"Pisces","Ketu":"Scorpio"},
        "chrome_d10": {"Ascendant":"Sagittarius","Sun":"Capricorn","Moon":"Leo","Mars":"Scorpio","Mercury":"Aries","Jupiter":"Aries","Venus":"Pisces","Saturn":"Aquarius","Rahu":"Capricorn","Ketu":"Leo"},
        "chrome_sav_labeled": {"Aries":25,"Taurus":24,"Gemini":25,"Cancer":32,"Leo":31,"Virgo":28,"Libra":29,"Scorpio":28,"Sagittarius":26,"Capricorn":29,"Aquarius":25,"Pisces":35}
    },
    "SMH_Trading_2000-12-20_09:30": {
        "dt": "2000-12-20 09:30:00",
        "chrome_d9":  {"Ascendant":"Aries","Sun":"Taurus","Moon":"Sagittarius","Mars":"Scorpio","Mercury":"Aries","Jupiter":"Pisces","Venus":"Cancer","Saturn":"Capricorn","Rahu":"Aries","Ketu":"Scorpio"},
        "chrome_d10": {"Ascendant":"Sagittarius","Sun":"Capricorn","Moon":"Sagittarius","Mars":"Libra","Mercury":"Scorpio","Jupiter":"Aries","Venus":"Pisces","Saturn":"Capricorn","Rahu":"Capricorn","Ketu":"Cancer"},
        "chrome_sav_labeled": {"Aries":27,"Taurus":26,"Gemini":24,"Cancer":24,"Leo":33,"Virgo":26,"Libra":36,"Scorpio":31,"Sagittarius":26,"Capricorn":23,"Aquarius":27,"Pisces":34}
    },
    "XME_Conception_2006-06-19_12:00": {
        "dt": "2006-06-19 12:00:00",
        "chrome_d9":  {"Ascendant":"Libra","Sun":"Sagittarius","Moon":"Sagittarius","Mars":"Scorpio","Mercury":"Libra","Jupiter":"Libra","Venus":"Libra","Saturn":"Scorpio","Rahu":"Cancer","Ketu":"Aries"},
        "chrome_d10": {"Ascendant":"Pisces","Sun":"Cancer","Moon":"Aries","Mars":"Leo","Mercury":"Pisces","Jupiter":"Taurus","Venus":"Capricorn","Saturn":"Cancer","Rahu":"Capricorn","Ketu":"Cancer"},
        "chrome_sav_labeled": {"Aries":34,"Taurus":35,"Gemini":23,"Cancer":21,"Leo":35,"Virgo":25,"Libra":29,"Scorpio":26,"Sagittarius":20,"Capricorn":33,"Aquarius":24,"Pisces":32}
    },
}

print("=" * 110)
print("FINAL COMPREHENSIVE AUDIT: Chrome Agent vs FIXED Python Backend")
print("=" * 110)

total_pass = total_fail = 0

for case_label, case_data in CHROME_CASES.items():
    backend = calc_chart(case_data["dt"])
    
    print(f"\n{'━'*110}")
    print(f"  CASE: {case_label} | Asc={backend['asc_sign']}")
    print(f"{'━'*110}")

    # --- D9 ---
    print(f"\n  [D9 NAVAMSA]  {'Planet':<14} {'CHROME':>15} {'BACKEND':>15}  STATUS")
    print(f"  {'-'*60}")
    for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu","Ascendant"]:
        cv = case_data["chrome_d9"].get(p,"N/A")
        bv = backend["D9"].get(p,"N/A")
        ok = "✅" if cv==bv else "❌"
        if cv==bv: total_pass+=1
        else: total_fail+=1
        print(f"  {'':6}{p:<14} {cv:>15} {bv:>15}  {ok}")

    # --- D10 ---
    print(f"\n  [D10 DASAMSA]  {'Planet':<14} {'CHROME':>15} {'BACKEND':>15}  STATUS")
    print(f"  {'-'*60}")
    for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu","Ascendant"]:
        cv = case_data["chrome_d10"].get(p,"N/A")
        bv = backend["D10"].get(p,"N/A")
        ok = "✅" if cv==bv else "❌"
        if cv==bv: total_pass+=1
        else: total_fail+=1
        print(f"  {'':6}{p:<14} {cv:>15} {bv:>15}  {ok}")

    # --- SAV: try both absolute and from-asc and report which matches better ---
    chrome_sav = case_data["chrome_sav_labeled"]
    abs_score = sum(1 for s,v in chrome_sav.items() if backend["SAV_abs"].get(s)==v)
    asc_score = sum(1 for s,v in chrome_sav.items() if backend["SAV_from_asc"].get(s)==v)

    print(f"\n  [SARVASHTAKVARGA]  Chrome vs Backend")
    print(f"  Absolute-zodiac match: {abs_score}/12  |  Ascendant-relative match: {asc_score}/12")
    best = backend["SAV_abs"] if abs_score >= asc_score else backend["SAV_from_asc"]
    print(f"  {'Sign':<14} {'CHROME':>8} {'BACKEND':>8}  STATUS")
    print(f"  {'-'*44}")
    for sign, cv in chrome_sav.items():
        bv = best.get(sign, "?")
        ok = "✅" if cv==bv else f"❌({cv-bv:+d})"
        if cv==bv: total_pass+=1
        else: total_fail+=1
        print(f"  {sign:<14} {cv:>8} {bv:>8}  {ok}")

print(f"\n{'='*110}")
print(f"  GRAND TOTAL: {total_pass} PASS / {total_fail} FAIL  ({total_pass/(total_pass+total_fail)*100:.1f}% match rate)")
print(f"{'='*110}")


# CRITICAL BUG FIX #17: Ensure swisseph is closed
import atexit
atexit.register(swe.close)
