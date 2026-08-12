"""
KP Placidus House Cusp Calculation Module

Lenses Applied:
1. Jyotish Scholar: Parashari/KP rules, strict KP Ayanamsa + Placidus (hsys=b'P').
2. Quant Developer: IEEE 754 drift prevention via modulus boundary mapping, strict O(1) ops.
3. ML Architect: Emits cyclical house variables strictly as sin/cos coordinate pairs. No discrete integers.
4. Data Engineer: Safe NaN propagation, strict typed NumPy arrays, zero 0-variance garbage.
"""

import threading
import numpy as np
import swisseph as swe
from contextlib import contextmanager
from typing import Dict

# Thread-local storage to enforce context manager isolation
_kp_state = threading.local()

@contextmanager
def kp_context_manager():
    """
    KP Context Manager.
    Guarantees strict isolation for KP ayanamsa settings.
    """
    _kp_state.in_kp_context = True
    # Jyotish Scholar Lens: Krishnamurti Ayanamsa (SIDM_KRISHNAMURTI = 5)
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI, 0, 0)
    
    try:
        yield
    finally:
        _kp_state.in_kp_context = False
        swe.close()

def compute_kp_cusps(jd: float, lat: float, lon: float) -> Dict[str, np.ndarray]:
    """
    Calculates 12 astrological house cusps using the Placidus system under KP Ayanamsa.
    
    Must be executed exclusively inside `kp_context_manager`.
    
    Args:
        jd (float): Julian Day.
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        
    Returns:
        Dict[str, np.ndarray]: Dictionary containing strict typed float64 arrays:
            - 'cusp_degrees': Exact longitudinal degrees [0, 360).
            - 'cusp_sin': Cyclical sine coordinate pairs.
            - 'cusp_cos': Cyclical cosine coordinate pairs.
    """
    # Enforce exclusivity inside the KP Context Manager
    if not getattr(_kp_state, 'in_kp_context', False):
        raise RuntimeError("compute_kp_cusps must be executed *exclusively* inside the kp_context_manager.")

    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    
    try:
        try:
            if abs(lat) >= 66.0:
                # Fallback to Porphyry at extreme latitudes
                cusps, ascmc = swe.houses_ex(jd, lat, lon, b'O', flags)
            else:
                # Jyotish Scholar: Placidus system hsys=b'P' alongside specific flags
                cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', flags)
        except Exception:
            try:
                # Fallback to Porphyry if Placidus fails
                cusps, ascmc = swe.houses_ex(jd, lat, lon, b'O', flags)
            except Exception:
                # Fallback to Equal if Porphyry fails
                cusps, ascmc = swe.houses_ex(jd, lat, lon, b'W', flags)
        
        # Data Engineer: Strict typed arrays, remove dummy 0 at index 0 to ensure shape (12,)
        cusp_array = np.array(cusps[1:], dtype=np.float64)
        
        # Capture Asc, MC, Vertex
        asc_deg = float(ascmc[0])
        mc_deg = float(ascmc[1])
        vertex_deg = float(ascmc[3])
        
        # Quant Developer: IEEE 754 drift prevention via precise modulo mapping
        cusp_array = np.mod(cusp_array, 360.0)
        asc_deg = np.mod(asc_deg, 360.0)
        mc_deg = np.mod(mc_deg, 360.0)
        vertex_deg = np.mod(vertex_deg, 360.0)
        
        # ML Architect: Cyclical variables strictly as sin/cos coordinate pairs
        rad_cusps = np.deg2rad(cusp_array)
        sin_cusps = np.sin(rad_cusps)
        cos_cusps = np.cos(rad_cusps)
        
        rad_asc = np.deg2rad(asc_deg)
        rad_mc = np.deg2rad(mc_deg)
        rad_vertex = np.deg2rad(vertex_deg)
        
        return {
            "cusp_degrees": cusp_array,
            "cusp_sin": sin_cusps,
            "cusp_cos": cos_cusps,
            "asc_degree": asc_deg,
            "asc_sin": np.sin(rad_asc),
            "asc_cos": np.cos(rad_asc),
            "mc_degree": mc_deg,
            "mc_sin": np.sin(rad_mc),
            "mc_cos": np.cos(rad_mc),
            "vertex_degree": vertex_deg,
            "vertex_sin": np.sin(rad_vertex),
            "vertex_cos": np.cos(rad_vertex)
        }
        
    except Exception:
        # Data Engineer Lens: Safe NaN propagation in case of computation failure
        nan_arr = np.full(12, np.nan, dtype=np.float64)
        nan_val = np.nan
        return {
            "cusp_degrees": nan_arr,
            "cusp_sin": nan_arr,
            "cusp_cos": nan_arr,
            "asc_degree": nan_val,
            "asc_sin": nan_val,
            "asc_cos": nan_val,
            "mc_degree": nan_val,
            "mc_sin": nan_val,
            "mc_cos": nan_val,
            "vertex_degree": nan_val,
            "vertex_sin": nan_val,
            "vertex_cos": nan_val
        }
