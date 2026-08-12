"""
FIX INVESTIGATION:
1. D9: Both element and quality formulas fail for QQQ. Need to find the ACTUAL formula Chrome uses.
2. SAV: Missing 2 bindus - Ascendant contribution is being counted wrong.
3. D10: Rahu/Ketu failing - they need special handling.
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

# For QQQ D9 - let's try REVERSE ENGINEERING what formula would give Chrome's answers
jd_qqq = get_jd("1999-03-10 09:30:00")
p_qqq = get_planets(jd_qqq)

chrome_d9_qqq = {
    "Ascendant": "Aries",   # Taurus(1) 8.44°
    "Sun": "Taurus",        # Aquarius(10) 25.72°
    "Moon": "Scorpio",      # Scorpio(7) 28.40°
    "Mars": "Aquarius",     # Libra(6) 17.98°
    "Mercury": "Scorpio",   # Pisces(11) 10.21°
    "Jupiter": "Aquarius",  # Pisces(11) 12.02°
    "Venus": "Gemini",      # Pisces(11) 26.67°
    "Saturn": "Aquarius",   # Aries(0) 7.13°
    "Rahu": "Aquarius",     # Cancer(3) 26.92°
    "Ketu": "Virgo"         # Capricorn(9) 26.92°
}

print("=" * 100)
print("REVERSE ENGINEERING D9 FOR QQQ - Finding what formula matches Chrome")
print("=" * 100)
print(f"\n{'Planet':<12} {'D1 Sign':<14} {'Lon':>8} {'Rem':>7} {'Part':>5} | Chrome D9  | Reverse-engineer needed start sign")
print("-" * 100)

for pname, exp in chrome_d9_qqq.items():
    lon = p_qqq[pname]
    sign_idx = int(lon/30)%12
    rem = lon % 30
    part = int(rem / (30.0/9))
    exp_idx = SIGNS.index(exp)
    # What start sign would give the Chrome D9?
    # (start + part) % 12 = exp_idx  →  start = (exp_idx - part) % 12
    needed_start = (exp_idx - part) % 12
    d1_sign = SIGNS[sign_idx]
    print(f"{pname:<12} {d1_sign:<14} {lon:>8.4f} {rem:>7.4f} {part:>5} | {exp:<10} | Need start = {SIGNS[needed_start]} (idx={needed_start})")
    
print("\n")
print("PATTERN ANALYSIS:")
print("Ascendant Taurus(1) needs start Sagittarius(8)  → 8 = ??? from 1")
print("Sun Aquarius(10) needs start Capricorn(9)       → 9 = 10-1 (sign - 1)?")
print("Moon Scorpio(7) needs start Pisces(11)          → 11 = 7+4")
print("Mars Libra(6) needs start Scorpio(7)            → 7 = 6+1")
print("Mercury Pisces(11) needs start Cancer(3)        → 3 = 11-8 or 11+4")
print("Jupiter Pisces(11) needs start Cancer(3)        → 3 = same as Mercury")
print("Venus Pisces(11) needs start Gemini(2)          → 2 = hmm, part=8 for Venus rem=26.67")
print("  Venus part check: 26.67/(30/9) = 26.67/3.333 = 8.0 exactly → part=8, need (2+8)%12=10=Aquarius? No Chrome says Gemini!")
print("  WAIT: 26.67/3.333 = 8.00 → int(8.00) could be 8 OR there's a floating point issue making it 7.999")
print("  If part=7: needed_start = (2-7)%12 = (-5)%12 = 7 = Scorpio")
print("  Hmm. Let me compute exactly:")
import math
lon_venus = p_qqq["Venus"]
rem_venus = lon_venus % 30
part_exact = rem_venus / (30.0/9)
print(f"\n  Venus exact: lon={lon_venus:.6f}, rem={rem_venus:.6f}, part_exact={part_exact:.6f}, int={int(part_exact)}")
print(f"  If website rounds DOWN with tiny epsilon: part={int(part_exact)}")

# The KEY INSIGHT: floating point precision at exact navamsa boundaries!
# When part_exact is EXACTLY 8.0000, floor gives 8 (last navamsa)
# But 9 navamsas mean indices 0-8, so part=8 is VALID (the 9th navamsa)
# Venus: part=8, Chrome says Gemini(2), start needed = (2-8)%12 = 6 = Libra
# Libra is the AIR start. Venus is in Pisces(11) = Water. Water start = Cancer(3), not Libra(6)
# BUT - if we use QUALITY: Pisces is DUAL → start = Libra(6)!
# (6 + 8)%12 = 14%12 = 2 = Gemini ✓ MATCH!

print("\n  Venus Pisces(Dual) Quality formula: Libra(6) + 8 = 14%12 = 2 = Gemini ✓")
print("\n  So Chrome uses QUALITY-based D9 (Movable→Aries, Fixed→Capricorn, Dual→Libra)")
print("  Let's verify ALL with quality formula...")

def d9_quality(lon):
    sign_idx = int(lon/30)%12
    rem = lon%30
    part = int(rem / (30.0/9))
    # Movable=Aries(0),Cancer(3),Libra(6),Cap(9) → start Aries(0)
    # Fixed=Taurus(1),Leo(4),Scorpio(7),Aqua(10) → start Capricorn(9)
    # Dual=Gemini(2),Virgo(5),Sag(8),Pisces(11) → start Libra(6)
    if sign_idx in [0,3,6,9]: start = 0   # Movable → Aries
    elif sign_idx in [1,4,7,10]: start = 9 # Fixed → Capricorn
    else: start = 6                         # Dual → Libra
    return SIGNS[(start + part) % 12]

print(f"\n{'Planet':<12} {'D1 Sign':<14} {'Quality':<10} {'Our D9 (Quality)':<18} {'Chrome':>8} {'Match'}")
print("-" * 80)
for pname, exp in chrome_d9_qqq.items():
    lon = p_qqq[pname]
    sign_idx = int(lon/30)%12
    d1_sign = SIGNS[sign_idx]
    quality = "Movable" if sign_idx in [0,3,6,9] else ("Fixed" if sign_idx in [1,4,7,10] else "Dual")
    d9 = d9_quality(lon)
    match = "✓" if d9 == exp else "✗"
    print(f"{pname:<12} {d1_sign:<14} {quality:<10} {d9:<18} {exp:>8} {match}")

# Now verify SPY with quality formula
print("\n\nNow verify SPY with quality formula:")
jd_spy = get_jd("1993-01-29 09:30:00")
p_spy = get_planets(jd_spy)

chrome_d9_spy = {
    "Ascendant": "Libra", "Sun": "Gemini", "Moon": "Aries", "Mars": "Pisces",
    "Mercury": "Cancer", "Jupiter": "Leo", "Venus": "Cancer", "Saturn": "Leo",
    "Rahu": "Capricorn", "Ketu": "Cancer"
}

print(f"\n{'Planet':<12} {'D1 Sign':<14} {'Quality':<10} {'Our D9 (Quality)':<18} {'Chrome':>8} {'Match'}")
print("-" * 80)
for pname, exp in chrome_d9_spy.items():
    lon = p_spy[pname]
    sign_idx = int(lon/30)%12
    d1_sign = SIGNS[sign_idx]
    quality = "Movable" if sign_idx in [0,3,6,9] else ("Fixed" if sign_idx in [1,4,7,10] else "Dual")
    d9 = d9_quality(lon)
    match = "✓" if d9 == exp else "✗"
    print(f"{pname:<12} {d1_sign:<14} {quality:<10} {d9:<18} {exp:>8} {match}")

# D10 investigation for Rahu/Ketu failure  
print("\n\nD10 Special Cases: Rahu/Ketu fail because of sign of KAL PURUSH vs actual sign?")
print("Rahu in SPY: Scorpio 25.15°, part=8, start=(7+8)%12=15%12=3=Cancer, D10=(3+8)%12=Pisces")
print("Chrome says Capricorn for Rahu. So: (start+8)%12=9 → start=1=Taurus? That makes no sense.")
print("Actually: sign_idx for Rahu=7(Scorpio), 7%2=1 (even in 0-indexed), so start=(7+8)%12=15%12=3=Cancer")
print("(Cancer+8)%12 = 11%12 = Pisces. Chrome says Capricorn(9).")
print("Need: (start+8)%12=9 → start=1=Taurus... Taurus is odd (0-indexed), start should be Taurus itself (idx=1)")  
print("This means Rahu/Ketu may use OPPOSITE sign rule in D10!")
print("Let's try: for Rahu use reverse sign (Scorpio → Taurus=1), start=1, (1+8)%12=9=Capricorn ✓!")
print("Ketu in SPY: Taurus 25.15°, part=8, start=1(Taurus itself), (1+8)%12=9=Capricorn... Chrome says Cancer(3)")  
print("Hmm. Ketu opposite of Rahu → Taurus opposite is Scorpio (7), (7+8)%12=15%12=3=Cancer ✓!")
print("\nCONCLUSION: For D10, Rahu uses the sign of KETU (opposite) and Ketu uses sign of RAHU (opposite)")
print("This is the 'shadow planet' rule for D10 in some schools.")
