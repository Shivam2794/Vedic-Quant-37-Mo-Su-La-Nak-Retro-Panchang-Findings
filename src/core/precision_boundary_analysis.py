"""
PRECISION D9 AND D10 BOUNDARY INVESTIGATION
For every mismatch, trace the exact longitude and identify the formula error.
"""
import sys, swisseph as swe
from datetime import datetime
import pytz
sys.stdout.reconfigure(encoding='utf-8')

swe.set_ephe_path(None)
swe.set_sid_mode(swe.SIDM_LAHIRI)

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

def get_exact_lons(dt_string):
    ny_tz = pytz.timezone('America/New_York')
    dt_naive = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
    dt_utc = ny_tz.localize(dt_naive).astimezone(pytz.utc)
    utc_hour = dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, utc_hour)
    flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH
    
    PLANET_IDS = {"Sun":swe.SUN,"Moon":swe.MOON,"Mars":swe.MARS,"Mercury":swe.MERCURY,
                  "Jupiter":swe.JUPITER,"Venus":swe.VENUS,"Saturn":swe.SATURN,"Rahu":swe.MEAN_NODE}
    pos = {}
    for p, pid in PLANET_IDS.items():
        res = swe.calc_ut(jd, pid, flags)
        pos[p] = res[0][0]
    pos["Ketu"] = (pos["Rahu"] + 180.0) % 360.0
    houses, ascmc = swe.houses_ex(jd, 40.7128, -74.0060, b'W', flags)
    pos["Ascendant"] = ascmc[0]
    return pos

# ===========================================================
# D10 PRECISE BOUNDARY ANALYSIS
# ===========================================================
# Classical Parashari D10 rules:
# Odd Sanskrit signs (Aries=1,Gem=3,Leo=5,Lib=7,Sag=9,Aq=11):
#   0-indexed: 0,2,4,6,8,10  → start from SAME sign
#   formula: (si + part) % 12
#
# Even Sanskrit signs (Tau=2,Can=4,Vir=6,Sc=8,Cap=10,Pis=12):
#   0-indexed: 1,3,5,7,9,11 → start from 9th sign from it
#   formula: (si + 8 + part) % 12

print("=" * 100)
print("D10 BOUNDARY TRACE — Every Confirmed Failure")
print("=" * 100)

# Cases where Chrome D10 is known reliable (XLK, XLC, trading dates where Chrome read text)
# Confirmed D10 mismatches from final_comparison.py output:
# XLK Conception: Rahu (our=Leo, Chrome=Virgo)
# XLK Trading: Rahu (our=Leo, Chrome=Leo ✅), check all
# SMH Trading: Mars(our=Scorpio, Chrome=Libra), Mercury(our=Sagittarius, Chrome=Scorpio)

D10_CONFIRMED_FAILURES = [
    # (case_dt, planet, chrome_d10, label)
    ("1998-12-16 12:00:00", "Rahu",    "Virgo",    "XLK Conc Rahu Leo 01°21'"),
    ("1998-12-22 09:30:00", "Rahu",    "Leo",      "XLK Trade Rahu Leo 01°03'"),
    ("2000-12-20 09:30:00", "Mars",    "Libra",    "SMH Trade Mars Libra 04°22'"),
    ("2000-12-20 09:30:00", "Mercury", "Scorpio",  "SMH Trade Mercury Sag 02°14'"),
    ("2015-10-06 12:00:00", "Moon",    "Taurus",   "XLRE Conc Moon Cancer 09°46'"),
    ("2006-06-19 12:00:00", "Moon",    "Aries",    "XME Conc Moon Pisces 18°23'"),
    ("2006-06-19 12:00:00", "Jupiter", "Taurus",   "XME Conc Jupiter Libra 15°28'"),
    ("2018-06-18 12:00:00", "Ascendant","Aries",   "XLC Conc Asc Leo 22°16'"),
    ("2018-06-19 09:30:00", "Ascendant","Libra",   "XLC Trade Asc Cancer 23°30'"),
]

# Current formula
def d10_current(lon):
    si = int(lon/30) % 12
    part = int((lon % 30) / 3.0)
    if si % 2 == 0:
        return si, part, SIGNS[(si + part) % 12]
    else:
        return si, part, SIGNS[(si + 8 + part) % 12]

# Try alternative: what if even signs start from 9th (same formula) but odd starts from same sign + 0 (no shift for part=0)?
# Or what if the ROUNDING is ceil not floor?
def d10_ceil(lon):
    si = int(lon/30) % 12
    deg = lon % 30
    # Use ceiling-based part
    part = int((deg + 0.001) / 3.0)
    part = min(part, 9)
    if si % 2 == 0:
        return SIGNS[(si + part) % 12]
    else:
        return SIGNS[(si + 8 + part) % 12]

# What if for even signs we use si+9 instead of si+8?
def d10_v2(lon):
    si = int(lon/30) % 12
    part = int((lon % 30) / 3.0)
    if si % 2 == 0:
        return SIGNS[(si + part) % 12]
    else:
        return SIGNS[(si + 9 + part) % 12]  # si+9 instead of si+8

# What if part is 1-indexed (part+1)?
def d10_1indexed(lon):
    si = int(lon/30) % 12
    part = int((lon % 30) / 3.0) + 1  # 1-indexed
    if si % 2 == 0:
        return SIGNS[(si + part) % 12]
    else:
        return SIGNS[(si + 8 + part) % 12]

for dt_str, planet, chrome_expected, label in D10_CONFIRMED_FAILURES:
    lons = get_exact_lons(dt_str)
    lon = lons[planet]
    si = int(lon/30) % 12
    deg_in_sign = lon % 30
    part = int(deg_in_sign / 3.0)
    arcmin_in_part = (deg_in_sign % 3.0) * 60

    si_name = SIGNS[si]
    parity = "ODD(Sanskrit)" if si % 2 == 0 else "EVEN(Sanskrit)"
    
    si_cur, part_cur, r_cur = d10_current(lon)
    r_v2 = d10_v2(lon)
    r_1idx = d10_1indexed(lon)
    r_ceil = d10_ceil(lon)
    
    chrome_idx = SIGNS.index(chrome_expected)
    our_idx = SIGNS.index(r_cur)
    diff = (chrome_idx - our_idx) % 12
    
    print(f"\n  {label}")
    print(f"  lon={lon:.6f}  sign={si_name}({si}) {parity}  deg_in_sign={deg_in_sign:.6f}")
    print(f"  part={part} (boundary at {part*3}°-{(part+1)*3}°, {arcmin_in_part:.1f}' into part)")
    print(f"  Current:  {r_cur}  |  v2(si+9): {r_v2}  |  1-indexed: {r_1idx}  |  ceil: {r_ceil}  |  Chrome: {chrome_expected}")
    
    which = []
    if r_cur == chrome_expected: which.append("CURRENT")
    if r_v2 == chrome_expected: which.append("V2(si+9)")
    if r_1idx == chrome_expected: which.append("1INDEXED")
    if r_ceil == chrome_expected: which.append("CEIL")
    
    if which:
        print(f"  => MATCH via: {', '.join(which)}")
    else:
        print(f"  => NONE MATCH. Chrome={chrome_expected}(idx={chrome_idx}), Ours={r_cur}(idx={our_idx}), Diff={diff} signs")
        # Try to work backwards: what exact longitude would produce Chrome's result?
        start = si if si % 2 == 0 else (si + 8) % 12
        needed_part = (chrome_idx - start) % 12
        min_lon = si * 30 + needed_part * 3
        max_lon = si * 30 + (needed_part + 1) * 3
        print(f"  => Chrome result requires lon in [{min_lon:.1f}°, {max_lon:.1f}°) = {SIGNS[si]} {needed_part*3}°-{(needed_part+1)*3}°")
        print(f"  => But actual lon={lon:.4f}° = {SIGNS[si]} {int(deg_in_sign)}°{int((deg_in_sign%1)*60)}'")

print("\n")
print("=" * 100)
print("D9 PRECISE BOUNDARY TRACE — Confirmed Failures (XLK where Chrome read text correctly)")
print("=" * 100)

# XLK Conception D9 mismatches: Mars(our=Gemini, Chrome=Capricorn), Mercury(our=Virgo, Chrome=Sagittarius), Asc(our=Gemini, Chrome=Aries)
D9_CONFIRMED_FAILURES = [
    ("1998-12-16 12:00:00", "Mars",      "Capricorn",  "XLK Conc Mars Virgo 16°42'"),
    ("1998-12-16 12:00:00", "Mercury",   "Sagittarius","XLK Conc Mercury Scorpio 09°38'"),
    ("1998-12-16 12:00:00", "Ascendant", "Aries",      "XLK Conc Asc Aquarius 29°26'"),
    ("1998-12-22 09:30:00", "Moon",      "Taurus",     "XLK Trade Moon Capricorn 19°07'"),
    ("1998-12-22 09:30:00", "Mars",      "Taurus",     "XLK Trade Mars Virgo 19°47'"),
    ("2018-06-18 12:00:00", "Sun",       "Gemini",     "XLC Conc Sun Gemini 03°16'"),
    ("2018-06-18 12:00:00", "Moon",      "Cancer",     "XLC Conc Moon Leo 10°13'"),
    ("2018-06-19 09:30:00", "Sun",       "Leo",        "XLC Trade Sun Gemini 04°07'"),
    ("2018-06-19 09:30:00", "Moon",      "Scorpio",    "XLC Trade Moon Leo 22°46'"),
    ("2018-06-19 09:30:00", "Mercury",   "Aries",      "XLC Trade Mercury Gemini 19°24'"),
]

# Current D9 formula: int(lon / (10/3)) % 12
def d9_current(lon):
    return int(lon / (10.0/3.0)) % 12, SIGNS[int(lon / (10.0/3.0)) % 12]

# Alternative: What if it's int(lon / 3.3334) % 12 (slightly different divisor)?
def d9_alt1(lon):
    return SIGNS[int(lon / 3.3334) % 12]

# Alternative: round instead of floor?
def d9_alt2(lon):
    return SIGNS[round(lon / (10.0/3.0)) % 12]

# Alternative: use lon+0.5 before floor?
def d9_alt3(lon):
    return SIGNS[int((lon + 0.5) / (10.0/3.0)) % 12]

for dt_str, planet, chrome_expected, label in D9_CONFIRMED_FAILURES:
    lons = get_exact_lons(dt_str)
    lon = lons[planet]
    
    nav_raw = lon / (10.0/3.0)
    nav_int = int(nav_raw)
    nav_frac = nav_raw - nav_int
    
    nav_idx_cur, r_cur = d9_current(lon)
    r_alt1 = d9_alt1(lon)
    r_alt2 = d9_alt2(lon)
    r_alt3 = d9_alt3(lon)
    
    chrome_idx = SIGNS.index(chrome_expected)
    diff = (chrome_idx - nav_idx_cur) % 12
    
    # Arcminutes within the current navamsa (each navamsa = 200 arcmin)
    arcmin_into_nav = (nav_raw - nav_int) * (10.0/3.0) * 60
    
    print(f"\n  {label}")
    print(f"  lon={lon:.6f}  nav_raw={nav_raw:.6f}  nav_int={nav_int}  nav_frac={nav_frac:.6f}")
    print(f"  {arcmin_into_nav:.1f}' into navamsa (200' total per navamsa)")
    print(f"  Current D9={r_cur}(nav={nav_int%12})  Chrome={chrome_expected}(nav_needed={chrome_idx}?)")
    print(f"  Diff = {diff} navamsas")
    
    which = []
    if r_cur == chrome_expected: which.append("CURRENT")
    if r_alt1 == chrome_expected: which.append("ALT1(3.3334)")
    if r_alt2 == chrome_expected: which.append("ALT2(round)")
    if r_alt3 == chrome_expected: which.append("ALT3(lon+0.5)")
    
    if which:
        print(f"  => MATCH via: {', '.join(which)}")
    else:
        # What nav_int would give the Chrome result?
        for offset in range(-6, 7):
            candidate = (nav_int + offset) % 12
            if candidate == chrome_idx:
                needed_nav_int = nav_int + offset
                needed_lon = needed_nav_int * (10.0/3.0)
                print(f"  => Chrome requires nav_int={needed_nav_int} (offset={offset:+d}), corresponding to lon={needed_lon:.2f} ({SIGNS[int(needed_lon/30)%12]} {int(needed_lon%30):.0f}°)")
        print(f"  => NO FORMULA MATCHES")


# CRITICAL BUG FIX #17: Ensure swisseph is closed
import atexit
atexit.register(swe.close)
