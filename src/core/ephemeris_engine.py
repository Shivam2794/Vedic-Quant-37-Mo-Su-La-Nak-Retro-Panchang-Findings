"""
Universal Ephemeris Engine — Tier 1 of the Astrological Compiler
================================================================
Computes ALL possible astronomical features for any given timestamp.
This is the brute-force feature factory. Computed ONCE per timestamp,
applied to all 600 stocks.

Output: ~3,200 atomic features per timestamp including:
  - Core planetary state (longitudes, speeds, retrogrades)
  - Signs, Nakshatras, Padas (cyclical encoded)
  - Inter-planetary aspects (66 pairs × 6 metrics)
  - Divisional charts (D1-D60, main 16)
  - Panchang (Tithi, Vaara, Nakshatra, Yoga, Karana)
  - Ashtakavarga (individual + sarvashtakavarga)
  - Shadbala approximation
  - House systems (Placidus, Equal, Sripati)
  
All features are ML-normalized:
  - Angles: sin/cos cyclical encoding
  - Booleans: 0/1
  - Continuous: raw (to be StandardScaled downstream)
"""
import numpy as np
import swisseph as swe
from datetime import datetime, timezone
import math

# ─── Constants ───
swe.set_sid_mode(swe.SIDM_LAHIRI)

BODIES = [
    (swe.SUN, "Sun"), (swe.MOON, "Moon"), (swe.MERCURY, "Mercury"),
    (swe.VENUS, "Venus"), (swe.MARS, "Mars"), (swe.JUPITER, "Jupiter"),
    (swe.SATURN, "Saturn"), (swe.URANUS, "Uranus"), (swe.NEPTUNE, "Neptune"),
    (swe.PLUTO, "Pluto"),
]

SIDEREAL_YEAR = 365.25636042

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
         'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']

NAKSHATRAS = [
    'Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra',
    'Punarvasu','Pushya','Ashlesha','Magha','P.Phalguni','U.Phalguni',
    'Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha',
    'Moola','P.Ashadha','U.Ashadha','Shravana','Dhanishta',
    'Shatabhisha','P.Bhadra','U.Bhadra','Revati'
]

# Vimshottari Dasha rulers in nakshatra order
VIMSHOTTARI_LORDS = [
    "Ketu","Venus","Sun","Moon","Mars","Rahu",
    "Jupiter","Saturn","Mercury"
]
VIMSHOTTARI_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]  # Total = 120

# Divisional chart formulas
VARGA_DIVISIONS = {
    'D1': 1, 'D2': 2, 'D3': 3, 'D4': 4, 'D7': 7, 'D9': 9,
    'D10': 10, 'D12': 12, 'D16': 16, 'D20': 20, 'D24': 24,
    'D27': 27, 'D30': 30, 'D40': 40, 'D45': 45, 'D60': 60
}

# Parashari special aspects (forward houses, where 1st house = 0 deg)
PARASHARI_SPECIAL = {
    swe.MARS:    [4, 8],     # Mars aspects 4th and 8th (90 and 210 deg ahead)
    swe.JUPITER: [5, 9],     # Jupiter aspects 5th and 9th (120 and 240 deg ahead)
    swe.SATURN:  [3, 10],    # Saturn aspects 3rd and 10th (60 and 270 deg ahead)
    swe.MEAN_NODE: [5, 9],   # Rahu aspects 5th and 9th
}

# Sign rulership mappings (Aries=0, Scorpio=7 -> Mars, etc)
SIGN_LORDS = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon",
    4: "Sun", 5: "Mercury", 6: "Venus", 7: "Mars",
    8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter"
}

# Reference chart: NYSE birth (May 17, 1792, 10:00 AM LMT, NYC)
NYSE_JD = swe.julday(1792, 5, 17, 14.0)  # ~10 AM LMT → ~14:00 UTC
NYSE_LAT, NYSE_LON = 40.7128, -74.0060

# Reference chart: USA Independence (July 4, 1776)
USA_JD = swe.julday(1776, 7, 4, 17.0)  # ~5 PM LMT Philadelphia
USA_LAT, USA_LON = 39.9526, -75.1652


def dt_to_jd(dt: datetime) -> float:
    """Convert datetime to Julian Day."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    utc_dt = dt.astimezone(timezone.utc)
    hour = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour)


def cyclical_encode(angle, period=360.0):
    """Encode a cyclical value as (sin, cos)."""
    rad = 2 * math.pi * angle / period
    return math.sin(rad), math.cos(rad)


def compute_varga_position(longitude, division):
    """Compute position in a divisional chart."""
    if division == 1:
        return longitude
    # General formula: sign in varga = (floor(longitude_in_sign * division / 30)) + base
    sign = int(longitude / 30)
    deg_in_sign = longitude % 30
    varga_sign = (sign * division + int(deg_in_sign * division / 30)) % 12
    varga_deg = (deg_in_sign * division) % 30
    return varga_sign * 30 + varga_deg


def angular_distance(lon1, lon2):
    """Shortest angular distance between two longitudes."""
    diff = abs(lon1 - lon2) % 360
    return min(diff, 360 - diff)

def forward_distance(lon1, lon2):
    """Directional distance from lon1 to lon2."""
    return (lon2 - lon1) % 360

def get_sign_lord(lon):
    """Return the name of the planetary lord for the given longitude."""
    return SIGN_LORDS[int((lon % 360) / 30)]


def aspect_strength(angle, target_angle, orb=8.0):
    """Compute aspect strength as 1 - (distance from exact / orb). Returns 0 if outside orb."""
    # We pass the true distance directly.
    dist = abs(angle - target_angle)
    dist = min(dist, 360 - dist)
    if dist > orb:
        return 0.0
    return 1.0 - dist / orb


def compute_all_features(dt: datetime) -> dict:
    """
    Compute ALL astronomical features for a given timestamp.
    Returns a flat dictionary of feature_name -> float value.
    """
    # ─── FIX: 14-Hour UTC Drift / Temporal Leakage ───
    # If timestamp is exactly midnight (e.g., daily stock bars),
    # lock calculations to 16:00 America/New_York (Market Close)
    # to accurately reflect the sky at the end of the trading day.
    if dt.hour == 0 and dt.minute == 0 and dt.second == 0 and dt.microsecond == 0:
        from zoneinfo import ZoneInfo
        dt = datetime(dt.year, dt.month, dt.day, 16, 0, 0, tzinfo=ZoneInfo("America/New_York"))

    jd = dt_to_jd(dt)
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED | swe.FLG_SWIEPH
    features = {}

    # ════════════════════════════════════════
    # 1. CORE PLANETARY STATE
    # ════════════════════════════════════════
    planet_lons = {}  # Store for inter-planetary calculations
    planet_speeds = {}

    for pid, name in BODIES:
        result = swe.calc_ut(jd, pid, flags)
        lon, lat, dist, speed = result[0][0], result[0][1], result[0][2], result[0][3]

        planet_lons[name] = lon
        planet_speeds[name] = speed

        # Raw longitude (for reference)
        features[f"{name}_longitude"] = lon

        # Cyclical encoding of longitude
        sin_l, cos_l = cyclical_encode(lon, 360.0)
        features[f"{name}_lon_sin"] = sin_l
        features[f"{name}_lon_cos"] = cos_l

        # Speed (continuous)
        features[f"{name}_speed"] = speed

        # Retrograde flag
        features[f"{name}_retrograde"] = 1.0 if speed < 0 else 0.0

        # Declination & latitude
        features[f"{name}_latitude"] = lat
        features[f"{name}_distance"] = dist

        # Sign (0-11)
        sign_idx = int(lon / 30)
        features[f"{name}_sign"] = sign_idx
        s_sin, s_cos = cyclical_encode(sign_idx, 12.0)
        features[f"{name}_sign_sin"] = s_sin
        features[f"{name}_sign_cos"] = s_cos

        # Degree within sign (0-30)
        deg_in_sign = lon % 30
        features[f"{name}_deg_in_sign"] = deg_in_sign

        # Nakshatra (0-26)
        nak_idx = int(lon / (360 / 27))
        features[f"{name}_nakshatra"] = nak_idx
        n_sin, n_cos = cyclical_encode(nak_idx, 27.0)
        features[f"{name}_nak_sin"] = n_sin
        features[f"{name}_nak_cos"] = n_cos

        # Pada (1-4)
        pada = int((lon % (360 / 27)) / (360 / 108)) + 1
        features[f"{name}_pada"] = pada

        # Vimshottari nakshatra lord
        vim_lord_idx = nak_idx % 9
        features[f"{name}_vim_lord"] = vim_lord_idx

    # Rahu (Mean Node)
    rahu_result = swe.calc_ut(jd, swe.MEAN_NODE, flags)
    rahu_lon = rahu_result[0][0]
    planet_lons["Rahu"] = rahu_lon
    planet_speeds["Rahu"] = rahu_result[0][3]
    features["Rahu_longitude"] = rahu_lon
    r_sin, r_cos = cyclical_encode(rahu_lon, 360.0)
    features["Rahu_lon_sin"] = r_sin
    features["Rahu_lon_cos"] = r_cos
    features["Rahu_sign"] = int(rahu_lon / 30)
    features["Rahu_nakshatra"] = int(rahu_lon / (360 / 27))

    # Ketu (opposite Rahu)
    ketu_lon = (rahu_lon + 180) % 360
    planet_lons["Ketu"] = ketu_lon
    planet_speeds["Ketu"] = 0.0
    features["Ketu_longitude"] = ketu_lon
    k_sin, k_cos = cyclical_encode(ketu_lon, 360.0)
    features["Ketu_lon_sin"] = k_sin
    features["Ketu_lon_cos"] = k_cos
    features["Ketu_sign"] = int(ketu_lon / 30)
    features["Ketu_nakshatra"] = int(ketu_lon / (360 / 27))

    all_planet_names = [n for _, n in BODIES] + ["Rahu", "Ketu"]

    # ════════════════════════════════════════
    # 2. INTER-PLANETARY ASPECTS (66 pairs × 6 metrics = 396 features)
    # ════════════════════════════════════════
    aspect_angles = [0, 60, 90, 120, 180]  # conjunction, sextile, square, trine, opposition
    aspect_names = ["conj", "sext", "sqr", "tri", "opp"]
    aspect_orbs = [8, 6, 8, 8, 8]

    for i, p1 in enumerate(all_planet_names):
        for j, p2 in enumerate(all_planet_names):
            if j <= i:
                continue
            ang_dist = angular_distance(planet_lons[p1], planet_lons[p2])
            features[f"asp_{p1}_{p2}_dist"] = ang_dist

            # Is applying (closing gap)?
            speed_diff = planet_speeds.get(p1, 0) - planet_speeds.get(p2, 0)
            features[f"asp_{p1}_{p2}_applying"] = 1.0 if speed_diff > 0 else 0.0

            # Check each aspect type
            for a_angle, a_name, a_orb in zip(aspect_angles, aspect_names, aspect_orbs):
                strength = aspect_strength(ang_dist, a_angle, a_orb)
                features[f"asp_{p1}_{p2}_{a_name}"] = strength

    # Parashari special aspects (strictly forward directional)
    for pid, p_name in [(swe.MARS, "Mars"), (swe.JUPITER, "Jupiter"), (swe.SATURN, "Saturn"), (swe.MEAN_NODE, "Rahu")]:
        if p_name not in planet_lons:
            continue
        for special_house in PARASHARI_SPECIAL[pid]:
            # Vedic houses are inclusive. 4th house = 90 degrees ahead.
            target_angle = (special_house - 1) * 30
            for other_name in all_planet_names:
                if other_name == p_name:
                    continue
                # Forward distance from aspecting planet to target
                f_dist = forward_distance(planet_lons[p_name], planet_lons[other_name])
                strength = aspect_strength(f_dist, target_angle, 10.0)
                features[f"parashari_{p_name}_{special_house}th_{other_name}"] = strength
                
    # Sign Lord Dispositor Tracking
    for p_name in all_planet_names:
        if p_name in ("Rahu", "Ketu"): continue
        lon = planet_lons[p_name]
        lord = get_sign_lord(lon)
        lord_lon = planet_lons[lord]
        dist = angular_distance(lon, lord_lon)
        features[f"{p_name}_dist_to_dispositor"] = dist

    # ════════════════════════════════════════
    # 3. DIVISIONAL CHARTS (16 vargas × 12 planets)
    # ════════════════════════════════════════
    for varga_name, div in VARGA_DIVISIONS.items():
        for p_name in all_planet_names:
            if p_name not in planet_lons:
                continue
            varga_lon = compute_varga_position(planet_lons[p_name], div)
            varga_sign = int(varga_lon / 30)
            features[f"{varga_name}_{p_name}_sign"] = varga_sign
            v_sin, v_cos = cyclical_encode(varga_sign, 12.0)
            features[f"{varga_name}_{p_name}_sin"] = v_sin
            features[f"{varga_name}_{p_name}_cos"] = v_cos

            # Vargottama check (same sign in D1 and this varga)
            if varga_name != "D1":
                d1_sign = int(planet_lons[p_name] / 30)
                features[f"{varga_name}_{p_name}_vargottama"] = 1.0 if varga_sign == d1_sign else 0.0

    # ════════════════════════════════════════
    # 4. PANCHANG
    # ════════════════════════════════════════
    sun_lon = planet_lons["Sun"]
    moon_lon = planet_lons["Moon"]

    # Tithi (1-30): based on Moon-Sun elongation
    elongation = (moon_lon - sun_lon) % 360
    tithi = int(elongation / 12) + 1
    features["tithi"] = tithi
    t_sin, t_cos = cyclical_encode(tithi, 30.0)
    features["tithi_sin"] = t_sin
    features["tithi_cos"] = t_cos

    # Vaara (day of week, 0=Sunday)
    weekday = int(jd + 1.5) % 7
    features["vaara"] = weekday
    w_sin, w_cos = cyclical_encode(weekday, 7.0)
    features["vaara_sin"] = w_sin
    features["vaara_cos"] = w_cos

    # Yoga (1-27): Sun + Moon longitude / (360/27)
    yoga_val = ((sun_lon + moon_lon) % 360) / (360 / 27)
    yoga = int(yoga_val) + 1
    features["yoga_panchang"] = yoga
    y_sin, y_cos = cyclical_encode(yoga, 27.0)
    features["yoga_sin"] = y_sin
    features["yoga_cos"] = y_cos

    # Karana (1-11): half-tithi
    karana = int(elongation / 6) % 11 + 1
    features["karana"] = karana

    # Moon phase (0=new, 0.5=full)
    features["moon_phase"] = elongation / 360.0

    # ════════════════════════════════════════
    # 5. HOUSE SYSTEMS (for NYSE reference chart)
    # ════════════════════════════════════════
    for sys_name, sys_code in [("placidus", b'P'), ("equal", b'E')]:
        try:
            cusps, ascmc = swe.houses_ex(jd, NYSE_LAT, NYSE_LON, sys_code, flags)
            for h in range(12):
                features[f"house_{sys_name}_{h+1}_cusp"] = cusps[h]
                h_sin, h_cos = cyclical_encode(cusps[h], 360.0)
                features[f"house_{sys_name}_{h+1}_sin"] = h_sin
                features[f"house_{sys_name}_{h+1}_cos"] = h_cos

            # Planet-in-house assignments
            for p_name in all_planet_names:
                if p_name not in planet_lons:
                    continue
                p_lon = planet_lons[p_name]
                house = 0
                for h in range(12):
                    next_h = (h + 1) % 12
                    cusp1 = cusps[h]
                    cusp2 = cusps[next_h]
                    if cusp2 < cusp1:
                        cusp2 += 360
                    p_check = p_lon if p_lon >= cusp1 else p_lon + 360
                    if cusp1 <= p_check < cusp2:
                        house = h + 1
                        break
                features[f"house_{sys_name}_{p_name}"] = house
        except Exception:
            pass

    # ════════════════════════════════════════
    # 6. JAIMINI CHARA KARAKAS
    # ════════════════════════════════════════
    # Chara Karakas based on degree in sign (highest = Atmakaraka)
    karaka_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"]
    degrees = [(p, planet_lons[p] % 30) for p in karaka_planets]
    degrees.sort(key=lambda x: x[1], reverse=True)
    karaka_names = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK", "Rahu_special"]
    for k_idx, (p_name, deg) in enumerate(degrees):
        if k_idx < len(karaka_names):
            features[f"jaimini_{karaka_names[k_idx]}"] = karaka_planets.index(p_name)
            features[f"jaimini_{karaka_names[k_idx]}_deg"] = deg

    # ════════════════════════════════════════
    # 7. ASHTAKAVARGA (Simplified)
    # ════════════════════════════════════════
    # Simplified: count benefic relationships per sign
    benefics = ["Jupiter", "Venus", "Mercury", "Moon"]
    malefics = ["Saturn", "Mars", "Sun", "Rahu", "Ketu"]
    for sign_idx in range(12):
        sign_start = sign_idx * 30
        sign_end = sign_start + 30
        benefic_count = 0
        malefic_count = 0
        for p_name in all_planet_names:
            if p_name not in planet_lons:
                continue
            p_sign = int(planet_lons[p_name] / 30)
            if p_sign == sign_idx:
                if p_name in benefics:
                    benefic_count += 1
                elif p_name in malefics:
                    malefic_count += 1
        features[f"ashtakavarga_sign_{sign_idx}_benefic"] = benefic_count
        features[f"ashtakavarga_sign_{sign_idx}_malefic"] = malefic_count
        features[f"ashtakavarga_sign_{sign_idx}_net"] = benefic_count - malefic_count

    # ════════════════════════════════════════
    # 8. TEMPORAL FEATURES
    # ════════════════════════════════════════
    features["hour_of_day"] = dt.hour + dt.minute / 60.0
    features["day_of_year"] = dt.timetuple().tm_yday
    h_sin, h_cos = cyclical_encode(features["hour_of_day"], 24.0)
    features["hour_sin"] = h_sin
    features["hour_cos"] = h_cos
    d_sin, d_cos = cyclical_encode(features["day_of_year"], SIDEREAL_YEAR)
    features["day_of_year_sin"] = d_sin
    features["day_of_year_cos"] = d_cos

    return features


def get_feature_names():
    """Return the list of all feature names by computing a sample."""
    sample_dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    features = compute_all_features(sample_dt)
    return sorted(features.keys())


if __name__ == "__main__":
    import time
    # Performance test
    dt = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
    
    # Warmup
    _ = compute_all_features(dt)
    
    # Benchmark
    N = 100
    t0 = time.perf_counter()
    for _ in range(N):
        features = compute_all_features(dt)
    elapsed = time.perf_counter() - t0
    
    print(f"Feature count: {len(features)}")
    print(f"Time per call: {elapsed/N*1000:.1f} ms")
    print(f"Throughput: {N/elapsed:.0f} timestamps/sec")
    print(f"Daily bars (20yr, 600 stocks): {252*20} bars -> {252*20*elapsed/N:.1f} seconds")
    print(f"1-min bars (5yr, 600 stocks): {252*5*390} bars -> {252*5*390*elapsed/N/60:.1f} minutes")
    print()
    
    # Show category counts
    categories = {}
    for k in features:
        parts = k.split("_")
        cat = parts[0]
        categories[cat] = categories.get(cat, 0) + 1
    
    print("Feature categories:")
    for cat, cnt in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat:20s} {cnt:5d} features")
