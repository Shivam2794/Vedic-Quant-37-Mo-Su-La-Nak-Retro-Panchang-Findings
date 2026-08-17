import math
import numpy as np
import swisseph as swe
from contextlib import contextmanager

@contextmanager
def kp_ayanamsha_context():
    """
    Context manager to guarantee the execution environment strictly uses KP Ayanamsha.
    Restores Lahiri Ayanamsha (standard Vedic) upon exit to prevent global state mutation.
    """
    # Save the current mode if possible, but standard is Lahiri (1). 
    # Swisseph uses SIDM_KRISHNAMURTI (5) for KP.
    try:
        swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
        yield
    finally:
        swe.set_sid_mode(swe.SIDM_LAHIRI)

DASHA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]

def _get_kp_lords(longitude: float) -> dict:
    if np.isnan(longitude):
        return {"star_lord": "", "sub_lord": ""}
        
    nak_idx = int(longitude / (360.0 / 27.0))
    star_lord_idx = nak_idx % 9
    star_lord = DASHA_LORDS[star_lord_idx]
    
    nak_start = nak_idx * (360.0 / 27.0)
    deg_in_nak = longitude - nak_start
    
    current_idx = star_lord_idx
    elapsed = 0.0
    sub_lord = ""
    for _ in range(9):
        sub_len = (DASHA_YEARS[current_idx] / 120.0) * (360.0 / 27.0)
        if elapsed + sub_len > deg_in_nak:
            sub_lord = DASHA_LORDS[current_idx]
            break
        elapsed += sub_len
        current_idx = (current_idx + 1) % 9
        
    return {"star_lord": star_lord, "sub_lord": sub_lord}

def compute_kp_longitudes(jd: float, lat: float = None, lon: float = None) -> dict:
    """
    Computes the 9 classical planetary longitudes under KP Ayanamsha.
    Uses True Nodes for Rahu/Ketu as required by precision Jyotish.
    Outputs exact degrees and cyclical variables strictly as sin/cos coordinate pairs.
    Handles safe NaN propagation.
    
    Args:
        jd (float): Julian Date (UT)
        lat (float): Latitude of the observer
        lon (float): Longitude of the observer
        
    Returns:
        dict: Typed dictionary with classical degrees and ML-ready cyclic coordinates.
    """
    if np.isnan(jd):
        return {}
        
    swe.set_ephe_path()
        
    base_flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    
    topo_valid = lat is not None and lon is not None and not np.isnan(lat) and not np.isnan(lon)
    if topo_valid:
        swe.set_topo(lon, lat, 0.0)
    
    # 9 Classical planets
    # Using True Node for Rahu as per Jyotish standard for precision
    planets = {
        'Sun': swe.SUN,
        'Moon': swe.MOON,
        'Mars': swe.MARS,
        'Mercury': swe.MERCURY,
        'Jupiter': swe.JUPITER,
        'Venus': swe.VENUS,
        'Saturn': swe.SATURN,
        'Rahu': swe.TRUE_NODE,
    }
    
    results = {}
    
    with kp_ayanamsha_context():
        rahu_lon = np.nan
        for p_name, p_id in planets.items():
            p_flags = base_flags
            if topo_valid and p_name != 'Rahu':
                p_flags |= swe.FLG_TOPOCTR
                
            try:
                res, _ = swe.calc_ut(jd, p_id, p_flags)
                lon_deg = res[0] % 360.0 # IEEE 754 drift prevention
                if p_name == 'Rahu':
                    rahu_lon = lon_deg
            except Exception:
                lon_deg = np.nan
                
            results[f"{p_name}_lon"] = float(lon_deg)
            if not np.isnan(lon_deg):
                rad = math.radians(lon_deg)
                results[f"{p_name}_sin"] = float(math.sin(rad))
                results[f"{p_name}_cos"] = float(math.cos(rad))
            else:
                results[f"{p_name}_sin"] = float('nan')
                results[f"{p_name}_cos"] = float('nan')
                
            # Populate nested dict for omni_vedic_fusion
            results[p_name] = _get_kp_lords(lon_deg)
            results[p_name]["longitude"] = float(lon_deg)
                
        # Ketu is diametrically opposite Rahu (180 degrees away)
        ketu_lon = np.nan
        if not np.isnan(rahu_lon):
            ketu_lon = (rahu_lon + 180.0) % 360.0
            
        results["Ketu_lon"] = float(ketu_lon)
        if not np.isnan(ketu_lon):
            rad = math.radians(ketu_lon)
            results["Ketu_sin"] = float(math.sin(rad))
            results["Ketu_cos"] = float(math.cos(rad))
        else:
            results["Ketu_sin"] = float('nan')
            results["Ketu_cos"] = float('nan')
            
        # Add Ketu sublords
        results["Ketu"] = _get_kp_lords(ketu_lon)
        results["Ketu"]["longitude"] = float(ketu_lon)
            
    return results


# CRITICAL BUG FIX #17: Ensure swisseph is closed
import atexit
atexit.register(swe.close)
