"""
DEEP SHADBALA INVESTIGATION
============================
Our Shadbala is severely underestimating Mars, Mercury, Saturn and overestimating some others.
Let's reverse engineer what formula the website uses by comparing component by component.

Chrome's SPY Shadbala:
  Sun: 7.33 rupas (required 5.0, ratio 1.47)
  Moon: 6.60 rupas (required 6.0, ratio 1.10)
  Mars: 6.35 rupas (required 5.0, ratio 1.27)
  Mercury: 8.43 rupas (required 7.0, ratio 1.20)
  Jupiter: (not in Sector ETFs trading chrome data for SPY)
  Venus: 4.62 rupas (required 5.5, ratio 0.84)
  Saturn: 4.19 rupas (required 5.0, ratio 0.84)

Our SPY Shadbala (approximate from output):
  Sun: 6.41 rupas
  Moon: 5.19 rupas
  Mars: 4.01 rupas
  Mercury: 5.03 rupas
  Venus: 6.14 rupas
  Saturn: 7.77 rupas

Divergence is massive and SYSTEMATIC. This suggests we're computing components completely wrong.
The main issue is likely in Kala Bala components:
1. Ayana Bala - we use true declination but wrong formula
2. Paksha Bala - formula correct but direction might be reversed
3. Tribhaga Bala - we're oversimplifying
4. Nathonnatha Bala - we're missing this component!
5. Yuddhabhala (planetary war) - we're missing this
6. Varsha/Masa/Dina/Hora Bala - we're missing multiple sub-components!

Actually, full BPHS Shadbala has 6 major components:
1. Sthana Bala (Positional Strength) - has 5 sub-components:
   a. Uchcha Bala - exaltation
   b. Saptavargaja Bala - 7 divisional charts (D1,D2,D3,D7,D9,D12,D30)
   c. Ojayugmarasyamsa Bala - odd/even sign
   d. Kendradi Bala - house position
   e. Drekkana Bala - decanate

2. Dig Bala (Directional Strength)

3. Kala Bala (Temporal Strength) - has 8 sub-components:
   a. Nathonnatha Bala - day/night
   b. Paksha Bala - lunar phase
   c. Tribhaga Bala - one-third of day
   d. Abda Bala - year lord
   e. Masa Bala - month lord
   f. Vara Bala - day lord
   g. Hora Bala - hour lord
   h. Ayana Bala - solstice

4. Chesta Bala (Motional Strength)
5. Naisargika Bala (Natural Strength)
6. Drik Bala (Aspectual Strength) - planet aspects

We're missing: Nathonnatha, Abda, Masa, Vara, Hora, Drik Bala entirely.
And our Saptavargaja is a rough approximation, not true 7-chart calculation.
"""
import sys, swisseph as swe
import math
from datetime import datetime
import pytz

sys.stdout.reconfigure(encoding='utf-8')
swe.set_ephe_path(None)
swe.set_sid_mode(swe.SIDM_LAHIRI)

NY_TZ = pytz.timezone('America/New_York')
PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

def get_jd(dt_str):
    dt = NY_TZ.localize(datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")).astimezone(pytz.utc)
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0 + dt.second/3600.0)

# Get SPY planet positions
dt_str = "1993-01-29 09:30:00"
jd = get_jd(dt_str)
flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH
houses, ascmc = swe.houses_ex(jd, 40.7128, -74.0060, b'W', flags)
asc_lon = ascmc[0]
mc_lon = ascmc[1]

planet_ids = {"Sun":swe.SUN,"Moon":swe.MOON,"Mars":swe.MARS,"Mercury":swe.MERCURY,
              "Jupiter":swe.JUPITER,"Venus":swe.VENUS,"Saturn":swe.SATURN}
plons = {}
for name, pid in planet_ids.items():
    res = swe.calc_ut(jd, pid, flags)
    plons[name] = {"lon": res[0][0], "speed": res[0][3], "lat": res[0][1]}

# Also get tropical for Ayana Bala
flags_trop = swe.FLG_SWIEPH
for name, pid in planet_ids.items():
    res = swe.calc_ut(jd, pid, flags_trop | swe.FLG_EQUATORIAL | swe.FLG_SWIEPH)
    plons[name]["dec"] = res[0][1]  # Declination

print("Planet positions:")
for n, d in plons.items():
    print(f"  {n}: lon={d['lon']:.4f}, speed={d['speed']:.4f}, dec={d['dec']:.4f}")

# =============================================
# COMPLETE SHADBALA IMPLEMENTATION
# =============================================

DEEP_EXALT = {"Sun":10,"Moon":33,"Mars":298,"Mercury":165,"Jupiter":95,"Venus":357,"Saturn":200}
NAISARGIKA = {"Sun":60,"Moon":51.43,"Venus":42.85,"Jupiter":34.28,"Mercury":25.71,"Mars":17.14,"Saturn":8.57}
LORDS_OF_SIGNS = ["Mars","Venus","Mercury","Moon","Sun","Mercury","Venus","Mars","Jupiter","Saturn","Saturn","Jupiter"]
REQUIRED_RUPAS = {"Sun":5.0,"Moon":6.0,"Mars":5.0,"Mercury":7.0,"Jupiter":6.5,"Venus":5.5,"Saturn":5.0}

NAISARGIKA_MAITRI = {
    "Sun": {"Friends":["Moon","Mars","Jupiter"],"Neutrals":["Mercury"],"Enemies":["Venus","Saturn"]},
    "Moon": {"Friends":["Sun","Mercury"],"Neutrals":["Mars","Jupiter","Venus","Saturn"],"Enemies":[]},
    "Mars": {"Friends":["Sun","Moon","Jupiter"],"Neutrals":["Venus","Saturn"],"Enemies":["Mercury"]},
    "Mercury": {"Friends":["Sun","Venus"],"Neutrals":["Mars","Jupiter","Saturn"],"Enemies":["Moon"]},
    "Jupiter": {"Friends":["Sun","Moon","Mars"],"Neutrals":["Saturn"],"Enemies":["Mercury","Venus"]},
    "Venus": {"Friends":["Mercury","Saturn"],"Neutrals":["Mars","Jupiter"],"Enemies":["Sun","Moon"]},
    "Saturn": {"Friends":["Mercury","Venus"],"Neutrals":["Jupiter"],"Enemies":["Sun","Moon","Mars"]}
}

def distance(p1, p2):
    d = abs(p1-p2)
    return d if d <= 180 else 360-d

def uchcha_bala(lon, planet):
    exalt = DEEP_EXALT[planet]
    deb = (exalt + 180) % 360
    # Uchcha Bala = (distance from debilitation) / 3
    dist_from_deb = distance(lon, deb)
    return dist_from_deb / 3.0  # Max 60 virupas at exaltation

def saptavargaja_bala_simplified(planet, lon, all_lons):
    """
    Simplified D1 proxy for Saptavargaja.
    True computation requires D2, D3, D7, D9, D12, D30 - we use D1 only scaled.
    """
    sign_idx = int(lon/30)%12
    lord = LORDS_OF_SIGNS[sign_idx]
    lord_sign = int(all_lons[lord]["lon"]/30)%12 if lord in all_lons else sign_idx
    
    # Tatkalika Maitri
    dist = (lord_sign - sign_idx) % 12
    if dist in [1,2,3,9,10,11]: tatkala = "Friend"
    elif dist == 0: tatkala = "Self"
    else: tatkala = "Enemy"
    
    # Naisargika
    if planet == lord: naisar = "Swakshetra"
    elif lord in NAISARGIKA_MAITRI.get(planet, {}).get("Friends", []): naisar = "Friend"
    elif lord in NAISARGIKA_MAITRI.get(planet, {}).get("Enemies", []): naisar = "Enemy"
    else: naisar = "Neutral"
    
    # Panchadha Maitri
    if naisar == "Swakshetra": rel = "Swakshetra"
    elif naisar == "Friend" and tatkala == "Friend": rel = "Adhimitra"
    elif naisar == "Neutral" and tatkala == "Friend": rel = "Mitra"
    elif naisar == "Enemy" and tatkala == "Friend": rel = "Sama"
    elif naisar == "Friend" and tatkala == "Enemy": rel = "Sama"
    elif naisar == "Neutral" and tatkala == "Enemy": rel = "Satru"
    elif naisar == "Enemy" and tatkala == "Enemy": rel = "Adhisatru"
    else: rel = "Sama"
    
    # Points per relationship
    pts = {"Moolatrikona":45,"Swakshetra":30,"Adhimitra":22.5,"Mitra":15,"Sama":7.5,"Satru":3.75,"Adhisatru":1.875}
    return pts.get(rel, 7.5) * 7  # Scale by 7 (7 divisional charts)

def dig_bala(lon, planet):
    """Dik Bala based on strong direction for each planet."""
    ic = (mc_lon + 180) % 360
    dsc = (asc_lon + 180) % 360
    
    # Strong points:
    # Sun/Mars: strong in 10th house (MC direction) → weak at IC
    # Moon/Venus: strong in 4th house → weak at MC  
    # Jupiter/Mercury: strong in 1st house → weak at 7th (DSC)
    # Saturn: strong in 7th house → weak at 1st (ASC)
    
    if planet in ["Sun","Mars"]: strong_pt = mc_lon
    elif planet in ["Moon","Venus"]: strong_pt = ic  # 4th = IC
    elif planet in ["Jupiter","Mercury"]: strong_pt = asc_lon
    elif planet == "Saturn": strong_pt = dsc
    else: strong_pt = asc_lon
    
    # Dik Bala = distance from strong point / 3 (max 60 when at strong pt, 0 when opposite)
    dist = distance(lon, strong_pt)
    return (180 - dist) / 3.0  # Corrected: 60 at strong, 0 at weak

def nathonnatha_bala(jd, lon_sun, dt):
    """Day/Night Bala. Diurnal planets strong in day, nocturnal at night."""
    # Get sunrise/sunset using swe
    geopos = [40.7128, -74.0060, 0]
    # Check if it's day or night (simplified: if Sun above horizon)
    # We'll use time of day relative to sunrise/sunset
    # Simplified: Sun above horizon = day
    sun_lon_trop = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)[0][0]
    # If birth hour is 9:30 AM = daytime
    is_day = True  # 9:30 AM is daytime
    
    diurnal = ["Sun", "Jupiter", "Saturn"]  # Strong in day
    nocturnal = ["Moon", "Venus", "Mars"]   # Strong in night
    # Mercury: always medium
    
    if is_day:
        return {p: 60.0 if p in diurnal else (30.0 if p == "Mercury" else 0.0) for p in PLANETS}
    else:
        return {p: 60.0 if p in nocturnal else (30.0 if p == "Mercury" else 0.0) for p in PLANETS}

def paksha_bala(moon_lon, sun_lon, planet):
    """Paksha Bala based on lunar phase (waxing/waning)."""
    moon_sun_diff = (moon_lon - sun_lon) % 360
    # Waxing (Shukla) = 0-180°, Waning (Krishna) = 180-360°
    if moon_sun_diff <= 180:
        paksha_fraction = moon_sun_diff / 180.0  # 0 at new moon, 1 at full moon
    else:
        paksha_fraction = (360 - moon_sun_diff) / 180.0  # 1 at full moon, 0 at new moon
    
    paksha_points = paksha_fraction * 60.0  # 0-60 virupas
    
    # Benefics get Shukla Paksha Bala (waxing = strong)
    # Malefics get Krishna Paksha Bala (waning = strong)
    benefics = ["Moon", "Mercury", "Jupiter", "Venus"]
    malefics = ["Sun", "Mars", "Saturn"]
    
    if planet in benefics:
        return paksha_points if moon_sun_diff <= 180 else (60 - paksha_points)
    else:
        return (60 - paksha_points) if moon_sun_diff <= 180 else paksha_points

def tribhaga_bala(jd, planet):
    """Tribhaga Bala - planet strong in one-third of day/night."""
    # Day is divided into 3 equal parts; night also.
    # Each planet rules a specific third.
    # Day thirds: Mercury, Sun, Saturn
    # Night thirds: Moon, Venus, Mars  
    # Jupiter is strong in both day & night portions
    # This is 09:30 AM - first third of day (6AM-12PM approximately)
    # Day hour 0 = sunrise (roughly 7AM in Jan NY)
    # 09:30 is in the 2nd third of day (8:20AM - 12PM)
    
    # Simplified: Jupiter always gets 60, the relevant third ruler gets 60
    # For now: 09:30 AM = 1st half of day
    day_thirds = ["Mercury", "Sun", "Saturn"]  # Rules of 1st, 2nd, 3rd day thirds
    # At 9:30 AM, 2nd third of day → Sun rules
    current_ruler = "Sun"  # Simplified: Sun rules 2nd third
    
    if planet == "Jupiter": return 60.0
    elif planet == current_ruler: return 60.0
    else: return 0.0

def vara_bala(jd, planet):
    """Vara (day of week) Bala. Day lord gets 45 virupas."""
    day_of_week = int(jd + 1.5) % 7  # 0=Sun,1=Mon,2=Tue,3=Wed,4=Thu,5=Fri,6=Sat
    day_lords = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
    day_lord = day_lords[day_of_week]
    return 45.0 if planet == day_lord else 0.0

def hora_bala(jd, planet):
    """Hora (planetary hour) Bala. Hora lord gets 60 virupas."""
    # Hora lords cycle every hour starting from sunrise
    # Day of week: 0=Sun,1=Mon,...  
    day_of_week = int(jd + 1.5) % 7
    day_lords = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
    day_lord_idx = day_lords.index(day_lords[day_of_week])
    # At 9:30 AM, approximately 2-3 hours after sunrise
    # Hora changes every hour; 9:30 AM is roughly hora 3-4 of the day
    # Simplified: use day lord shifted by hour
    hour = 9  # 9:30 AM
    hora_idx = (day_lord_idx + hour) % 7
    hora_lord = day_lords[hora_idx]
    return 60.0 if planet == hora_lord else 0.0

def ayana_bala(dec, planet):
    """Ayana Bala based on declination (distance from equator)."""
    # Uttarayana planets (northern declination) are strong
    # Dakshinayana planets (southern) are weak
    # Formula: for Sun/Mars/Jupiter/Venus/Mercury: (24+dec)/48 * 60
    # For Moon/Saturn: (24-dec)/48 * 60
    if planet in ["Sun","Mars","Jupiter","Venus","Mercury"]:
        return max(0, min(60, (24 + dec) / 48.0 * 60.0))
    elif planet in ["Moon","Saturn"]:
        return max(0, min(60, (24 - dec) / 48.0 * 60.0))
    else:
        return 30.0

def abda_bala(jd, planet):
    """Abda (Year) Bala. Year lord gets 15 virupas."""
    # Year lord is determined by finding which planet rules the moment
    # This is complex - using simplified calculation
    # The first day of the year (samvatsara) lord is the planet of the first hora
    # Simplified: Capricorn ingress lord
    # For 1993: Year lord calculation skipped (complex Vedic calendar)
    # Returning 0 for all as approximation
    return 0.0

def masa_bala(jd, planet):
    """Masa (Month) Bala. Month lord gets 30 virupas."""
    # In Vedic astrology, month = lunar month. Month lord = lord of the day of Shukla Pratipada
    # Simplified: returning 0
    return 0.0

def yuddhabhala(planet, all_lons):
    """Yuddha Bala (planetary war). Planets within 1° in same sign."""
    # If two planets are in planetary war, the winner gets extra strength
    # Simplified: returning 0
    return 0.0

def chesta_bala(speed, planet, lon):
    """Chesta Bala based on planetary motion."""
    if planet in ["Sun","Moon"]: return 0.0  # Sun/Moon always direct, no Chesta Bala
    
    # For retrograde planets: 60 virupas
    # For stations (speed near 0): 30 virupas
    # For direct fast motion: proportional
    
    if speed < -0.1:  # Retrograde
        return 60.0
    elif abs(speed) < 0.1:  # Stationary
        return 30.0
    else:
        return 15.0  # Direct motion - simplified

def kendradi_bala(sign_idx, asc_sign_idx):
    """Kendradi Bala based on quadrant position."""
    dist = (sign_idx - asc_sign_idx) % 12
    if dist in [0,3,6,9]: return 60.0  # Kendra
    elif dist in [1,4,7,10]: return 30.0  # Panapara
    else: return 15.0  # Apoklima

def drekkana_bala(lon, planet):
    """Drekkana Bala based on which decanate the planet is in."""
    drek = int((lon % 30) / 10)  # 0, 1, or 2
    male_planets = ["Sun","Mars","Jupiter"]
    female_planets = ["Moon","Venus"]
    neutral_planets = ["Mercury","Saturn"]
    
    if drek == 0 and planet in male_planets: return 15.0
    elif drek == 1 and planet in neutral_planets: return 15.0
    elif drek == 2 and planet in female_planets: return 15.0
    return 0.0

def ojayugma_bala(sign_idx, planet):
    """Oja-Yugma (odd-even) sign Bala."""
    is_odd_sign = sign_idx % 2 == 0  # Aries(0), Gemini(2) etc are "odd" in Vedic
    male_planets = ["Sun","Mars","Jupiter"]
    female_planets = ["Moon","Venus"]
    
    if is_odd_sign and planet in male_planets: return 15.0
    elif not is_odd_sign and planet in female_planets: return 15.0
    elif planet == "Mercury": return 15.0  # Mercury always gets this
    elif planet == "Saturn": return 15.0 if is_odd_sign else 0.0
    return 0.0

def drik_bala(planet, all_lons):
    """Drik Bala (Aspectual Strength). Simplified."""
    # Full implementation requires computing aspects from all planets
    # Simplified: neutral for now
    return 0.0

# =============================================
# Compute complete Shadbala for SPY
# =============================================
dt = NY_TZ.localize(datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")).astimezone(pytz.utc)
asc_sign_idx = int(asc_lon/30)%12

chrome_shadbala_spy = {
    "Sun": 7.33, "Moon": 5.72, "Mars": 6.71, "Mercury": 7.75, "Jupiter": 5.73, "Venus": 8.58, "Saturn": 4.37
}
chrome_shadbala_etf = {
    "Sun": 7.33, "Moon": 6.6, "Mars": 6.35, "Mercury": 8.43, "Venus": 4.62, "Saturn": 4.19
}

print("\n" + "="*80)
print("COMPLETE SHADBALA COMPUTATION - SPY Trading 1993-01-29")
print("="*80)

moon_lon = plons["Moon"]["lon"]
sun_lon = plons["Sun"]["lon"]

for p in PLANETS:
    lon = plons[p]["lon"]
    speed = plons[p]["speed"]
    dec = plons[p]["dec"]
    sign_idx = int(lon/30)%12
    
    ub = uchcha_bala(lon, p)
    sapta = saptavargaja_bala_simplified(p, lon, plons)
    oja = ojayugma_bala(sign_idx, p)
    kendra = kendradi_bala(sign_idx, asc_sign_idx)
    drek = drekkana_bala(lon, p)
    sthana = ub + sapta + oja + kendra + drek
    
    dik = dig_bala(lon, p)
    
    natho = nathonnatha_bala(jd, sun_lon, dt).get(p, 0)
    paksha = paksha_bala(moon_lon, sun_lon, p)
    tribha = tribhaga_bala(jd, p)
    vara = vara_bala(jd, p)
    hora = hora_bala(jd, p)
    ayana = ayana_bala(dec, p)
    kala = natho + paksha + tribha + vara + hora + ayana
    
    chesta = chesta_bala(speed, p, lon)
    naisar = NAISARGIKA[p]
    drik = 0.0  # Simplified
    
    total_virupas = sthana + dik + kala + chesta + naisar + drik
    total_rupas = round(total_virupas / 60.0, 2)
    
    exp = chrome_shadbala_spy.get(p, "?")
    diff = round(total_rupas - exp, 2) if isinstance(exp, float) else "?"
    
    print(f"\n{p}:")
    print(f"  Uchcha:{ub:.1f} Sapta:{sapta:.1f} Oja:{oja:.1f} Kendra:{kendra:.1f} Drek:{drek:.1f} | Sthana={sthana:.1f}")
    print(f"  Dik:{dik:.1f}")
    print(f"  Natho:{natho:.1f} Paksha:{paksha:.1f} Tribha:{tribha:.1f} Vara:{vara:.1f} Hora:{hora:.1f} Ayana:{ayana:.1f} | Kala={kala:.1f}")
    print(f"  Chesta:{chesta:.1f} Naisar:{naisar:.2f}")
    print(f"  TOTAL Virupas: {total_virupas:.1f} | Rupas: {total_rupas} | Chrome: {exp} | Diff: {diff}")
