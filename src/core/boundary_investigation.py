"""
DEEP BOUNDARY INVESTIGATION
============================
For each failing D9/D10 planet, we print the exact longitude, computed navamsa part,
and what the alternative formula gives. This proves which formula Chrome uses.
"""
import sys, swisseph as swe
from datetime import datetime
import pytz

sys.stdout.reconfigure(encoding='utf-8')
swe.set_ephe_path(None)
swe.set_sid_mode(swe.SIDM_LAHIRI)

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

NY_TZ = pytz.timezone('America/New_York')
def get_jd(dt_str):
    dt = NY_TZ.localize(datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")).astimezone(pytz.utc)
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0 + dt.second/3600.0)

def get_planets(jd, lat=40.7128, lon=-74.0060):
    flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH
    houses, ascmc = swe.houses_ex(jd, lat, lon, b'W', flags)
    planet_ids = {"Sun":swe.SUN,"Moon":swe.MOON,"Mars":swe.MARS,"Mercury":swe.MERCURY,
                  "Jupiter":swe.JUPITER,"Venus":swe.VENUS,"Saturn":swe.SATURN,"Rahu":swe.MEAN_NODE}
    p = {}
    for name, pid in planet_ids.items():
        res = swe.calc_ut(jd, pid, flags)
        p[name] = res[0][0]
    p["Ketu"] = (p["Rahu"] + 180) % 360
    p["Ascendant"] = ascmc[0]
    return p

def d9_sign_elem(lon):
    """Element-based (our current formula)"""
    sign_idx = int(lon/30)%12
    rem = lon%30
    part = int(rem/(30.0/9))
    start = [0,9,6,3][sign_idx%4]
    return SIGNS[(start+part)%12]

def d9_sign_quality(lon):
    """Quality-based (Movable/Fixed/Dual)"""
    sign_idx = int(lon/30)%12
    rem = lon%30
    part = int(rem/(30.0/9))
    # Movable=0,3,6,9 → start Aries(0); Fixed=1,4,7,10 → Cap(9); Dual=2,5,8,11 → Libra(6)
    quality_start = {0:0,3:0,6:0,9:0, 1:9,4:9,7:9,10:9, 2:6,5:6,8:6,11:6}
    start = quality_start[sign_idx]
    return SIGNS[(start+part)%12]

def d10_sign_even9(lon):
    """Odd=self, Even=9th (our current formula)"""
    sign_idx = int(lon/30)%12
    rem = lon%30
    part = int(rem/3.0)
    start = sign_idx if sign_idx%2==0 else (sign_idx+8)%12
    return SIGNS[(start+part)%12]

def d10_sign_alt(lon):
    """Alternative: Odd=self, Even=from 9th ahead (same as above but verify)"""
    sign_idx = int(lon/30)%12
    rem = lon%30
    part = int(rem/3.0)
    # For even signs (2,4,6,8,10,12 in 1-indexed) = idx 1,3,5,7,9,11
    # 9th from sign: if sign=Taurus(1), 9th=Capricorn(9). (1+8)=9 ✓
    if sign_idx%2 == 0:  # odd signs (1st, 3rd... = Aries, Gemini...)
        start = sign_idx
    else:  # even signs
        start = (sign_idx + 8) % 12
    return SIGNS[(start+part)%12]

# CHROME EXPECTED D9 FOR SPY
chrome_d9_spy = {
    "Ascendant": "Libra",  # Pisces(Asc) → Libra
    "Sun": "Gemini",       # Capricorn(Sun) → Gemini
    "Moon": "Aries",       # Aries(Moon) → Aries
    "Mars": "Pisces",      # Gemini(Mars) → Pisces
    "Mercury": "Cancer",   # Capricorn(Mercury) → Cancer
    "Jupiter": "Leo",      # Virgo(Jupiter) → Leo
    "Venus": "Cancer",     # Pisces(Venus) → Cancer
    "Saturn": "Leo",       # Capricorn(Saturn) → Leo
    "Rahu": "Capricorn",   # Scorpio(Rahu) → Capricorn
    "Ketu": "Cancer"       # Taurus(Ketu) → Cancer
}

jd_spy = get_jd("1993-01-29 09:30:00")
p_spy = get_planets(jd_spy)

print("=" * 90)
print("D9 BOUNDARY INVESTIGATION - SPY Trading 1993-01-29")
print("=" * 90)
print(f"{'Planet':<12} {'D1 Sign':<14} {'Lon':>8} {'Rem':>6} {'Part':>4} | {'Elem D9':<12} | {'Qual D9':<12} | Chrome")
print("-" * 90)

for pname, exp in chrome_d9_spy.items():
    lon = p_spy[pname]
    sign_idx = int(lon/30)%12
    rem = lon%30
    part = int(rem/(30.0/9))
    d9_e = d9_sign_elem(lon)
    d9_q = d9_sign_quality(lon)
    d1_sign = SIGNS[sign_idx]
    status_e = "✓" if d9_e == exp else "✗"
    status_q = "✓" if d9_q == exp else "✗"
    print(f"{pname:<12} {d1_sign:<14} {lon:>8.4f} {rem:>6.4f} {part:>4} | {d9_e:<10} {status_e}  | {d9_q:<10} {status_q}  | {exp}")

print("\n")
print("=" * 90)
print("D9 BOUNDARY INVESTIGATION - QQQ Trading 1999-03-10")
print("=" * 90)

chrome_d9_qqq = {
    "Ascendant": "Aries",
    "Sun": "Taurus",
    "Moon": "Scorpio",
    "Mars": "Aquarius",
    "Mercury": "Scorpio",
    "Jupiter": "Aquarius",
    "Venus": "Gemini",
    "Saturn": "Aquarius",
    "Rahu": "Aquarius",
    "Ketu": "Virgo"
}

jd_qqq = get_jd("1999-03-10 09:30:00")
p_qqq = get_planets(jd_qqq)

print(f"{'Planet':<12} {'D1 Sign':<14} {'Lon':>8} {'Rem':>6} {'Part':>4} | {'Elem D9':<12} | {'Qual D9':<12} | Chrome")
print("-" * 90)

for pname, exp in chrome_d9_qqq.items():
    lon = p_qqq[pname]
    sign_idx = int(lon/30)%12
    rem = lon%30
    part = int(rem/(30.0/9))
    d9_e = d9_sign_elem(lon)
    d9_q = d9_sign_quality(lon)
    d1_sign = SIGNS[sign_idx]
    status_e = "✓" if d9_e == exp else "✗"
    status_q = "✓" if d9_q == exp else "✗"
    print(f"{pname:<12} {d1_sign:<14} {lon:>8.4f} {rem:>6.4f} {part:>4} | {d9_e:<10} {status_e}  | {d9_q:<10} {status_q}  | {exp}")

# D10 investigation  
print("\n")
print("=" * 90)
print("D10 BOUNDARY INVESTIGATION - SPY Trading 1993-01-29")
print("=" * 90)

chrome_d10_spy = {
    "Ascendant": "Aquarius",
    "Sun": "Aquarius",
    "Moon": "Aries",
    "Mars": "Scorpio",
    "Mercury": "Pisces",
    "Jupiter": "Sagittarius",
    "Venus": "Scorpio",
    "Saturn": "Taurus",
    "Rahu": "Capricorn",
    "Ketu": "Cancer"
}

print(f"{'Planet':<12} {'D1 Sign':<14} {'Lon':>8} {'Rem':>6} {'Part':>4} | {'D10_even9':<14} | Chrome")
print("-" * 90)

for pname, exp in chrome_d10_spy.items():
    lon = p_spy[pname]
    sign_idx = int(lon/30)%12
    rem = lon%30
    part = int(rem/3.0)
    d10 = d10_sign_even9(lon)
    d1_sign = SIGNS[sign_idx]
    status = "✓" if d10 == exp else "✗"
    start = sign_idx if sign_idx%2==0 else (sign_idx+8)%12
    print(f"{pname:<12} {d1_sign:<14} {lon:>8.4f} {rem:>6.4f} {part:>4} | {d10:<12} {status}  | {exp}  (start={SIGNS[start]}+{part})")

print("\n")
print("=" * 90)
print("SAV DISCREPANCY INVESTIGATION - SPY Trading 1993-01-29")
print("=" * 90)

chrome_sav_spy = {"Aries":28,"Taurus":26,"Gemini":29,"Cancer":23,"Leo":26,"Virgo":31,
                  "Libra":27,"Scorpio":33,"Sagittarius":28,"Capricorn":25,"Aquarius":32,"Pisces":29}

BAV_RULES = {
    "Sun":     {"Sun":[1,2,4,7,8,9,10,11],"Moon":[3,6,10,11],"Mars":[1,2,4,7,8,9,10,11],"Mercury":[3,5,6,9,10,11,12],"Jupiter":[5,6,9,11],"Venus":[6,7,12],"Saturn":[1,2,4,7,8,9,10,11],"Ascendant":[3,4,6,10,11,12]},
    "Moon":    {"Sun":[3,6,7,8,10,11],"Moon":[1,3,6,7,10,11],"Mars":[2,3,5,6,9,10,11],"Mercury":[1,3,4,5,7,8,10,11],"Jupiter":[1,4,7,8,10,11,12],"Venus":[3,4,5,7,9,10,11],"Saturn":[3,5,6,11],"Ascendant":[3,6,10,11]},
    "Mars":    {"Sun":[3,5,6,10,11],"Moon":[3,6,11],"Mars":[1,2,4,7,8,10,11],"Mercury":[3,5,6,11],"Jupiter":[6,10,11,12],"Venus":[6,8,11,12],"Saturn":[1,4,7,8,9,10,11],"Ascendant":[1,3,6,10,11]},
    "Mercury": {"Sun":[5,6,9,11,12],"Moon":[2,4,6,8,10,11],"Mars":[1,2,4,7,8,9,10,11],"Mercury":[1,3,5,6,9,10,11,12],"Jupiter":[6,8,11,12],"Venus":[1,2,3,4,5,8,9,11],"Saturn":[1,2,4,7,8,9,10,11],"Ascendant":[1,2,4,6,8,10,11]},
    "Jupiter": {"Sun":[1,2,3,4,7,8,9,10,11],"Moon":[2,5,7,9,11],"Mars":[1,2,4,7,8,10,11],"Mercury":[1,2,4,5,6,9,10,11],"Jupiter":[1,2,3,4,7,8,10,11],"Venus":[2,5,6,9,10,11],"Saturn":[3,5,6,12],"Ascendant":[1,2,4,5,6,9,10,11]},
    "Venus":   {"Sun":[8,11,12],"Moon":[1,2,3,4,5,8,9,11,12],"Mars":[3,5,6,9,11,12],"Mercury":[3,5,6,9,11],"Jupiter":[5,8,9,10,11],"Venus":[1,2,3,4,5,8,9,10,11],"Saturn":[3,4,5,8,9,10,11],"Ascendant":[1,2,3,4,5,8,9,11]},
    "Saturn":  {"Sun":[1,2,4,7,8,10,11],"Moon":[3,6,11],"Mars":[3,5,6,10,11],"Mercury":[6,8,9,10,11,12],"Jupiter":[5,6,11,12],"Venus":[6,11,12],"Saturn":[3,5,6,11],"Ascendant":[1,3,4,6,10,11]}
}

def compute_bav(p_dict):
    SIGNS_L = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
    sign_idx = lambda name: int(p_dict[name]/30)%12
    bav = {planet: {s: 0 for s in SIGNS_L} for planet in BAV_RULES}
    for tgt, sources in BAV_RULES.items():
        for src, positions in sources.items():
            src_si = sign_idx(src)
            for pos in positions:
                target_si = (src_si + pos - 1) % 12
                bav[tgt][SIGNS_L[target_si]] += 1
    sav = {s: sum(bav[p][s] for p in BAV_RULES) for s in SIGNS_L}
    return bav, sav

bav_spy, sav_spy = compute_bav(p_spy)

print(f"\n{'Sign':<14} {'Our SAV':>8} {'Chrome SAV':>10} {'Diff':>6}")
print("-" * 40)
SIGNS_L = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
our_total = 0; chrom_total = 0
for s in SIGNS_L:
    our = sav_spy[s]
    exp = chrome_sav_spy.get(s, "?")
    diff = our - exp if isinstance(exp, int) else "?"
    our_total += our
    if isinstance(exp, int): chrom_total += exp
    flag = " ✓" if diff == 0 else f" ✗ off by {diff}"
    print(f"{s:<14} {our:>8} {exp:>10} {str(diff):>6} {flag}")
print(f"\nOur total SAV: {our_total}, Chrome total SAV: {chrom_total}")
print(f"Difference: {our_total - chrom_total}")
print(f"\nNote: Total SAV should always be 337 for 7 planets × 48 max bindus / 12 signs")
print(f"Our total: {our_total} (should be 337)")
print(f"Chrome total: {chrom_total}")
