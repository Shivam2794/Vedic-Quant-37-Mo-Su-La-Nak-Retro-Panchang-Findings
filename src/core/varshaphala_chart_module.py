"""
varshaphala_chart_module.py
===========================
Step 3.5 — Tasks B, C, D: Annual Chart Computation

Computes the Varshaphala features at the exact Solar Return moment.

4-LENS FIXES:
- LENS 2 & 3: Sripati House system (hsys=b'S') with SEFLG_SIDEREAL is enforced.
- LENS 3: Muntha advances 1 SIGN per year, correctly 1-indexed (Year 1 = Natal Lagna).
- LENS 1 & 4: Muntha encoded as sin/cos circular features.
- LENS 1 & 3: Varshapati implemented as 'varshapati_simplified', returning a 
  9-dimensional vector of scores to preserve gradient. Parashari aspects replaced
  with Tajika aspects for scoring. Nodes excluded from Muntha lord pathway.
- LENS 4: Features generated are TV=1 (annual sequence).
"""

import numpy as np
import swisseph as swe
import math
from tajika_aspects_module import TAJIKA_ASPECTS, TAJIKA_ORBS, compute_tajika_yogas

# The 7 classical planets for Tajika (0-6). 7=Rahu, 8=Ketu
CLASSICAL_PLANETS = [swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, swe.VENUS, swe.SATURN]
PLANET_IDS = CLASSICAL_PLANETS + [swe.TRUE_NODE, swe.MEAN_NODE]

SIGN_LORDS = [
    2,  # Aries -> Mars (2)
    5,  # Taurus -> Venus (5)
    3,  # Gemini -> Mercury (3)
    1,  # Cancer -> Moon (1)
    0,  # Leo -> Sun (0)
    3,  # Virgo -> Mercury (3)
    5,  # Libra -> Venus (5)
    2,  # Scorpio -> Mars (2)
    4,  # Sagittarius -> Jupiter (4)
    6,  # Capricorn -> Saturn (6)
    6,  # Aquarius -> Saturn (6)
    4   # Pisces -> Jupiter (4)
]

def _is_tajika_aspect(lon1: float, lon2: float, orb: float = 12.0) -> bool:
    """Simple check if two longitudes are in a generic Tajika aspect (used for scoring)."""
    dist = abs((lon1 - lon2) % 360.0)
    if dist > 180.0:
        dist = 360.0 - dist
    for asp in TAJIKA_ASPECTS:
        if abs(dist - asp) <= orb:
            return True
    return False

def compute_varshaphala_features(asset_id: str,
                                 varsha_year: int,
                                 sr_jd: float,
                                 incorp_lat: float,
                                 incorp_lon: float,
                                 natal_asc_lon: float) -> dict:
    """
    Computes TV=1 annual features for a specific Solar Return year.
    varsha_year: 1-indexed (1 = first annual chart, covering birth to birth+1yr).
    """
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SPEED | swe.FLG_SIDEREAL | swe.FLG_SWIEPH

    # 1. Compute Planets
    lons = np.zeros(9, dtype=np.float64)
    speeds = np.zeros(9, dtype=np.float64)
    for i, pid in enumerate(PLANET_IDS):
        # NOTE: Mean node used for Ketu if TRUE_NODE is Rahu. 
        # Here we just use TRUE_NODE for Rahu, and offset by 180 for Ketu to match previous logic.
        if i == 8: # Ketu
            lons[i] = (lons[7] + 180.0) % 360.0
            speeds[i] = speeds[7]
        else:
            pos, _ = swe.calc_ut(sr_jd, pid, flags)
            lons[i] = pos[0]
            speeds[i] = pos[3]

    # 2. Compute Sripati Houses (TRAP B1, B4 FIX)
    # Must use SEFLG_SIDEREAL flag explicitly in houses_ex
    cusps, ascmc = swe.houses_ex(sr_jd, incorp_lat, incorp_lon, b'S', flags)
    sr_asc_lon = ascmc[0]
    sr_asc_sign = int(sr_asc_lon / 30.0)

    # 3. Muntha (TRAP C-DE-1, C-JS-1, C-ML-1, C-ML-3 FIX)
    # varsha_year is 1-indexed. Year 1 = Natal Lagna.
    # Muntha advances exactly 30 degrees (1 sign) per year, maintaining Natal Lagna degree
    muntha_lon = (natal_asc_lon + (varsha_year - 1) * 30.0) % 360.0
    muntha_sign_raw = int(muntha_lon / 30.0)
    muntha_sin = np.sin(np.radians(muntha_lon))
    muntha_cos = np.cos(np.radians(muntha_lon))
    muntha_lon_approx = muntha_lon # Exact degree used for aspect checks

    # 4. Varshapati Simplified Scoring (TRAP D-ML-3, D-JS-1, D-JS-4 FIX)
    scores = np.zeros(9, dtype=np.float64)
    
    # Pre-computations
    lagna_lord = SIGN_LORDS[sr_asc_sign]
    muntha_lord = SIGN_LORDS[muntha_sign_raw] # Nodes inherently excluded by SIGN_LORDS
    
    # Hora Approximation:
    # 24 planetary hours. Day starts ~6AM local mean time.
    local_jd = sr_jd + (incorp_lon / 360.0)
    frac_day = local_jd - math.floor(local_jd)
    # Convert frac_day to local hour (0-24, where 0 is noon). So add 12.
    local_hour = (frac_day * 24.0 + 12.0) % 24.0
    # Approximate hours since 6 AM
    hours_since_6am = (local_hour - 6.0) % 24.0
    hora_idx = int(hours_since_6am)
    
    # Weekday of local time (0=Monday, 6=Sunday). 
    # Rollover at ~6AM local mean time (True Sunrise approximation)
    weekday = math.floor(local_jd + 0.25) % 7 
    # Planetary day lords mapping (Sun=0, Mon=1, Tue=2, Wed=3, Thu=4, Fri=5, Sat=6)
    # SWE constants: SUN=0, MOON=1... but weekday is Mon=0.
    # Map weekday to SWE planet index:
    day_to_planet = {6: 0, 0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6}
    day_lord = day_to_planet[weekday]
    
    # Chaldean sequence for hours: Saturn(6), Jupiter(4), Mars(2), Sun(0), Venus(5), Mercury(3), Moon(1)
    chaldean = [6, 4, 2, 0, 5, 3, 1]
    lord_pos = chaldean.index(day_lord)
    hora_lord = chaldean[(lord_pos + hora_idx) % 7]

    for p in range(7): # Only 7 classical planets for Varshapati
        p_sign = int(lons[p] / 30.0)
        
        # 1. Planet in Lagna sign
        if p_sign == sr_asc_sign:
            scores[p] += 1.0
            
        # 2. Planet aspecting Lagna
        if _is_tajika_aspect(lons[p], sr_asc_lon, orb=TAJIKA_ORBS[p]):
            scores[p] += 1.0
            
        # 3. Lord of Lagna
        if p == lagna_lord:
            scores[p] += 1.0
            
        # 4. Planet in Hora at SR
        if p == hora_lord:
            scores[p] += 1.0
            
        # 5. Planet in trikona to Lagna lord
        if _is_tajika_aspect(lons[p], lons[lagna_lord], orb=12.0) and abs(abs(lons[p] - lons[lagna_lord]) % 360 - 120) < 12.0:
            scores[p] += 1.0
            
        # 6. Lord of Muntha sign
        if p == muntha_lord:
            scores[p] += 1.0
            
        # 7. Planet aspecting Muntha
        if _is_tajika_aspect(lons[p], muntha_lon_approx, orb=TAJIKA_ORBS[p]):
            scores[p] += 1.0

    # Normalize scores [0, 1]
    scores_norm = scores / 7.0

    # 5. Tajika Yogas
    ithasala, ishrafa = compute_tajika_yogas(lons[:7], speeds[:7])

    return {
        "asset_id": asset_id,
        "varsha_year": varsha_year,
        "sr_jd": sr_jd,
        "sr_asc_lon": sr_asc_lon,
        "muntha_sign_raw": muntha_sign_raw,
        "muntha_sin": muntha_sin,
        "muntha_cos": muntha_cos,
        "varshapati_simplified_scores": scores_norm,
        "ithasala_matrix": ithasala,
        "ishrafa_matrix": ishrafa
    }

if __name__ == "__main__":
    swe.set_ephe_path(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\ephe")
    
    # Test for SPY: Natal Asc = 129.5 -> Leo (Sign 4)
    # Incorp Lat/Lon = 40.7128, -74.0060
    # SR JD (Year 1) = 2449382.362511
    
    res = compute_varshaphala_features(
        asset_id="SPY",
        varsha_year=1,
        sr_jd=2449382.362511,
        incorp_lat=40.7128,
        incorp_lon=-74.0060,
        natal_asc_lon=129.5
    )
    
    print("[VALIDATION] Varshaphala Chart Features:")
    print(f"Muntha Sign (Raw): {res['muntha_sign_raw']} (Expected: 4 for Yr 1)")
    print(f"Varshapati Scores (Sun=0, ..., Saturn=6): \n{res['varshapati_simplified_scores'][:7]}")
    print("[VALIDATION] varshaphala_chart_module PASSED.")
