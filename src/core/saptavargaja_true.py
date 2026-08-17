"""
IMPLEMENT TRUE SAPTAVARGAJA BALA (7-chart computation)
This is the most critical missing piece for accurate Shadbala.

The 7 charts: D1(Rasi), D2(Hora), D3(Drekkana), D7(Saptamsa), D9(Navamsa), D12(Dwadasamsa), D30(Trimsamsa)
Per chart max contribution:
  D1: 30 (own sign), 45 (moolatrikona), 60 (exaltation)  -- scaled to out of 45
  
Per BPHS the points for each relationship in each chart:
  Moolatrikona: 45 Sv, Own sign (Swakshetra): 30 Sv, Great Friend (Adhimitra): 22.5, Friend (Mitra): 15,
  Neutral (Sama): 7.5, Enemy (Satru): 3.75, Great Enemy (Adhisatru): 1.875

Total max per chart = 45 (Moolatrikona), usually averaged at 22.5-30
Grand max = 45 × 7 = 315 virupas (theoretical)

Let's compute TRUE Saptavargaja for SPY Saturn.
"""

import sys, swisseph as swe
from datetime import datetime
import pytz

sys.stdout.reconfigure(encoding='utf-8')
swe.set_ephe_path(None)
swe.set_sid_mode(swe.SIDM_LAHIRI)

NY_TZ = pytz.timezone('America/New_York')
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

def get_jd(dt_str):
    dt = NY_TZ.localize(datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")).astimezone(pytz.utc)
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0 + dt.second/3600.0)

flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH | swe.FLG_SPEED
jd = get_jd("1993-01-29 09:30:00")
houses, ascmc = swe.houses_ex(jd, 40.7128, -74.0060, b'W', swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
asc_lon = ascmc[0]

planet_ids = {"Sun":swe.SUN,"Moon":swe.MOON,"Mars":swe.MARS,"Mercury":swe.MERCURY,
              "Jupiter":swe.JUPITER,"Venus":swe.VENUS,"Saturn":swe.SATURN}
plons = {}
for name, pid in planet_ids.items():
    res = swe.calc_ut(jd, pid, flags)
    plons[name] = {"lon": res[0][0]}

LORDS = ["Mars","Venus","Mercury","Moon","Sun","Mercury","Venus","Mars","Jupiter","Saturn","Saturn","Jupiter"]
NAISARGIKA_MAITRI = {
    "Sun": {"Friends":["Moon","Mars","Jupiter"],"Neutrals":["Mercury"],"Enemies":["Venus","Saturn"]},
    "Moon": {"Friends":["Sun","Mercury"],"Neutrals":["Mars","Jupiter","Venus","Saturn"],"Enemies":[]},
    "Mars": {"Friends":["Sun","Moon","Jupiter"],"Neutrals":["Venus","Saturn"],"Enemies":["Mercury"]},
    "Mercury": {"Friends":["Sun","Venus"],"Neutrals":["Mars","Jupiter","Saturn"],"Enemies":["Moon"]},
    "Jupiter": {"Friends":["Sun","Moon","Mars"],"Neutrals":["Saturn"],"Enemies":["Mercury","Venus"]},
    "Venus": {"Friends":["Mercury","Saturn"],"Neutrals":["Mars","Jupiter"],"Enemies":["Sun","Moon"]},
    "Saturn": {"Friends":["Mercury","Venus"],"Neutrals":["Jupiter"],"Enemies":["Sun","Moon","Mars"]}
}
OWN_SIGNS = {
    "Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5],
    "Jupiter": [8, 11], "Venus": [1, 6], "Saturn": [9, 10]
}
MOOLATRIKONA = {"Sun":4,"Moon":1,"Mars":0,"Mercury":5,"Jupiter":8,"Venus":5,"Saturn":10}
EXALT_SIGNS = {"Sun":0,"Moon":1,"Mars":9,"Mercury":5,"Jupiter":3,"Venus":11,"Saturn":6}
DEBI_SIGNS = {"Sun":6,"Moon":7,"Mars":3,"Mercury":11,"Jupiter":9,"Venus":5,"Saturn":0}
SAPTA_PTS = {"Exalt":60,"Moolatrikona":45,"Swakshetra":30,"Adhimitra":22.5,"Mitra":15,"Sama":7.5,"Satru":3.75,"Adhisatru":1.875,"Debi":0}

def tatkalika(sign1, sign2):
    dist = (sign2 - sign1) % 12
    return "Friend" if dist in [1,2,3,9,10,11] else ("Self" if dist == 0 else "Enemy")

def get_rel(planet, sign_idx, lord_sign_idx):
    lord = LORDS[sign_idx]
    if sign_idx == EXALT_SIGNS.get(planet): return "Exalt"
    if sign_idx == DEBI_SIGNS.get(planet): return "Debi"
    if sign_idx == MOOLATRIKONA.get(planet) and planet not in ["Moon","Venus","Mercury"]: return "Moolatrikona"
    if planet == lord or sign_idx in OWN_SIGNS.get(planet, []): return "Swakshetra"
    tatkala = tatkalika(sign_idx, lord_sign_idx)
    if lord in NAISARGIKA_MAITRI.get(planet, {}).get("Friends", []): naisar = "Friend"
    elif lord in NAISARGIKA_MAITRI.get(planet, {}).get("Enemies", []): naisar = "Enemy"
    else: naisar = "Neutral"
    
    combos = {("Friend","Friend"):"Adhimitra",("Neutral","Friend"):"Mitra",("Enemy","Friend"):"Sama",
              ("Friend","Enemy"):"Sama",("Neutral","Enemy"):"Satru",("Enemy","Enemy"):"Adhisatru"}
    return combos.get((naisar, tatkala), "Sama")

def get_lord_sign(planet, all_lons):
    lord = LORDS[int(all_lons[planet]["lon"]/30)%12]
    return int(all_lons.get(lord, {"lon":0})["lon"]/30)%12

def d1_sign(lon):
    return int(lon/30)%12

def d2_sign(lon, planet):
    """Hora - Sun's sign for 1st 15°, Moon's sign for 2nd 15°"""
    sign_idx = int(lon/30)%12
    rem = lon % 30
    is_odd = sign_idx % 2 == 0  # Odd signs (Aries=0=odd, Taurus=1=even in BPHS even/odd)
    if rem < 15:  # First half
        return 4 if is_odd else 3  # Leo(4) for odd, Cancer(3) for even
    else:  # Second half
        return 3 if is_odd else 4  # Cancer for odd, Leo for even

def d3_sign(lon):
    """Drekkana - each 10° in D3 represents a sign"""
    sign_idx = int(lon/30)%12
    rem = lon % 30
    part = int(rem/10)  # 0,1,2
    starts = [sign_idx, (sign_idx+4)%12, (sign_idx+8)%12]
    return starts[part]

def d7_sign(lon):
    """Saptamsa"""
    sign_idx = int(lon/30)%12
    rem = lon % 30
    part = int(rem/(30.0/7))
    is_odd = sign_idx % 2 == 0
    start = sign_idx if is_odd else (sign_idx+6)%12
    return (start + part) % 12

def d9_sign(lon):
    """Navamsa - element based"""
    sign_idx = int(lon/30)%12
    rem = lon % 30
    part = int(rem/(30.0/9))
    start = [0,9,6,3][sign_idx%4]  # Fire→Aries, Earth→Cap, Air→Lib, Water→Can
    return (start + part) % 12

def d12_sign(lon):
    """Dwadasamsa"""
    sign_idx = int(lon/30)%12
    rem = lon % 30
    part = int(rem/(30.0/12))
    return (sign_idx + part) % 12

def d30_sign(lon, planet):
    """Trimsamsa - complex, different for odd/even signs"""
    sign_idx = int(lon/30)%12
    rem = lon % 30
    is_odd = sign_idx % 2 == 0
    
    # Trimsamsa lords for odd signs: Mars 0-5, Saturn 5-10, Jupiter 10-18, Mercury 18-25, Venus 25-30
    # For even signs: Venus 0-5, Mercury 5-12, Jupiter 12-20, Saturn 20-25, Mars 25-30
    if is_odd:
        if rem < 5: lord = "Mars"
        elif rem < 10: lord = "Saturn"
        elif rem < 18: lord = "Jupiter"
        elif rem < 25: lord = "Mercury"
        else: lord = "Venus"
    else:
        if rem < 5: lord = "Venus"
        elif rem < 12: lord = "Mercury"
        elif rem < 20: lord = "Jupiter"
        elif rem < 25: lord = "Saturn"
        else: lord = "Mars"
    
    # Trimsamsa sign = lord's own sign in D1
    lord_sign = OWN_SIGNS[lord][0]  # Use first own sign
    # For D30, actual sign = lord's D1 sign position
    return int(plons[lord]["lon"]/30)%12  # Simplified: lord's D1 sign

# Compute Saptavargaja for SPY planets
print("TRUE SAPTAVARGAJA BALA COMPUTATION - SPY Trading 1993-01-29")
print("="*80)
print(f"{'Planet':<10} {'D1':>6} {'D2':>6} {'D3':>6} {'D7':>6} {'D9':>6} {'D12':>6} {'D30':>6} | {'Total':>7} {'Rupas':>6}")
print("-"*80)

chrome_sat_total = 4.37 * 60  # = 262.2 virupas total
chrome_sat_sapta_est = 262.2 - 60 - 145 - 15 - 8.57  # subtract Dik + Kala + Chesta + Naisar
print(f"\nChrome Saturn total: 262.2 virupas. Estimated Saptavargaja = {chrome_sat_sapta_est:.1f}")
print(f"Our current D1-proxy: 210 (30 × 7). Need to be much lower.\n")

for pname in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]:
    lon = plons[pname]["lon"]
    lord_sign = get_lord_sign(pname, plons)
    
    d1 = d1_sign(lon)
    r1 = get_rel(pname, d1, lord_sign)
    
    d2 = d2_sign(lon, pname)
    r2 = get_rel(pname, d2, int(plons[LORDS[d2]]["lon"]/30)%12 if LORDS[d2] in plons else 0)
    
    d3 = d3_sign(lon)
    r3 = get_rel(pname, d3, int(plons[LORDS[d3]]["lon"]/30)%12 if LORDS[d3] in plons else 0)
    
    d7 = d7_sign(lon)
    r7 = get_rel(pname, d7, int(plons[LORDS[d7]]["lon"]/30)%12 if LORDS[d7] in plons else 0)
    
    d9 = d9_sign(lon)
    r9 = get_rel(pname, d9, int(plons[LORDS[d9]]["lon"]/30)%12 if LORDS[d9] in plons else 0)
    
    d12 = d12_sign(lon)
    r12 = get_rel(pname, d12, int(plons[LORDS[d12]]["lon"]/30)%12 if LORDS[d12] in plons else 0)
    
    d30 = d30_sign(lon, pname)
    r30 = get_rel(pname, d30, int(plons[LORDS[d30]]["lon"]/30)%12 if LORDS[d30] in plons else 0)
    
    pts1 = SAPTA_PTS.get(r1, 7.5)
    pts2 = SAPTA_PTS.get(r2, 7.5)
    pts3 = SAPTA_PTS.get(r3, 7.5)
    pts7 = SAPTA_PTS.get(r7, 7.5)
    pts9 = SAPTA_PTS.get(r9, 7.5)
    pts12 = SAPTA_PTS.get(r12, 7.5)
    pts30 = SAPTA_PTS.get(r30, 7.5)
    total = pts1+pts2+pts3+pts7+pts9+pts12+pts30
    
    print(f"{pname:<10} {pts1:>6.1f} {pts2:>6.1f} {pts3:>6.1f} {pts7:>6.1f} {pts9:>6.1f} {pts12:>6.1f} {pts30:>6.1f} | {total:>7.1f} {total/60:>6.2f}")
    print(f"           {SIGNS[d1][:5]:>6} {SIGNS[d2][:5]:>6} {SIGNS[d3][:5]:>6} {SIGNS[d7][:5]:>6} {SIGNS[d9][:5]:>6} {SIGNS[d12][:5]:>6} {SIGNS[d30][:5]:>6}")
    print(f"           {r1[:5]:>6} {r2[:5]:>6} {r3[:5]:>6} {r7[:5]:>6} {r9[:5]:>6} {r12[:5]:>6} {r30[:5]:>6}")
    print()


# CRITICAL BUG FIX #17: Ensure swisseph is closed
import atexit
atexit.register(swe.close)
