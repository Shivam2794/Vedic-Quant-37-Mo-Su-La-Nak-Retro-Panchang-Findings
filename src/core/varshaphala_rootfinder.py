"""
varshaphala_rootfinder.py
=========================
Step 3.5 — Task A: Solar Return Root Finder

Finds the EXACT Julian Day when the Sun returns to its natal SIDEREAL longitude
for each Varsha (year) over the lifetime of the asset.

4-LENS FRAMEWORK INSPECTION
----------------------------
🔴 ML Architect:
  - Returns a float64 numpy array of shape (N_YEARS,) of Solar Return JDs.
  - Each JD is accurate to within TOLERANCE = 1e-5 degrees (~1 second of time).

🔴 Data Engineer:
  - TRAP FIX (CRITICAL): The subagent identified that swe_set_sid_mode MUST be 
    asserted. We explicitly set swe.SIDM_LAHIRI before bisection.
  - CONVERGENCE: The search window is ±2 days. Bisection guaranteed to converge 
    within 50 iterations.
  - We use the SIDEREAL year (365.25636042 days) as the seed step since we are
    looking for sidereal returns.

🔴 Jyotish Scholar:
  - TRAP FIX (CRITICAL): As per Tajika Neelakanthi, the classical Varshapravesha 
    moment is defined as the Sun's return to its SIDEREAL natal degree. 
  - We use Lahiri Ayanamsha (default in Indian astrology).

🔴 Quant Developer:
  - Bisection handles 359° -> 0° wrap around correctly using signed angular diff.
  - Bracket sign-check added before bisection to prevent false convergence.
"""

import numpy as np
import swisseph as swe
import math

SIDEREAL_YEAR   = 365.25636042   # Days (exact sidereal year, used for sidereal return seed)
TOLERANCE_DEG   = 1e-5           # ~0.86 seconds of time for Sun
MAX_ITERATIONS  = 50             


def _get_sun_sidereal_lon(jd: float) -> float:
    """Returns sidereal Sun longitude in degrees (Lahiri)."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH
    pos, _ = swe.calc_ut(jd, swe.SUN, flags)
    return float(pos[0])


def _signed_angle_diff(lon_a: float, lon_b: float) -> float:
    """
    Returns the signed angular difference (lon_a - lon_b) in degrees,
    mapped to (-180, +180]. Handles 0°/360° wrap-around.
    """
    diff = (lon_a - lon_b) % 360.0
    if diff > 180.0:
        diff -= 360.0
    return diff


def find_solar_return_jd(birth_jd: float,
                          natal_sidereal_sun_lon: float,
                          year_number: int,
                          window_days: float = 2.0) -> float:
    if year_number < 1:
        raise ValueError(f"year_number must be >= 1, got {year_number}")

    # Seed: use SIDEREAL year for sidereal return approximation
    seed_jd  = birth_jd + year_number * SIDEREAL_YEAR
    jd_low   = seed_jd - window_days
    jd_high  = seed_jd + window_days

    # Set ayanamsa
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    diff_low  = _signed_angle_diff(_get_sun_sidereal_lon(jd_low),  natal_sidereal_sun_lon)
    diff_high = _signed_angle_diff(_get_sun_sidereal_lon(jd_high), natal_sidereal_sun_lon)

    if diff_low * diff_high > 0:
        jd_low   = seed_jd - 4.0
        jd_high  = seed_jd + 4.0
        diff_low  = _signed_angle_diff(_get_sun_sidereal_lon(jd_low),  natal_sidereal_sun_lon)
        diff_high = _signed_angle_diff(_get_sun_sidereal_lon(jd_high), natal_sidereal_sun_lon)
        if diff_low * diff_high > 0:
            raise RuntimeError(
                f"Solar Return bisection bracket failed for year {year_number}. "
                f"diff_low={diff_low:.4f}, diff_high={diff_high:.4f}."
            )

    # Bisection
    for iteration in range(MAX_ITERATIONS):
        jd_mid  = (jd_low + jd_high) / 2.0
        diff_mid = _signed_angle_diff(_get_sun_sidereal_lon(jd_mid), natal_sidereal_sun_lon)

        if abs(diff_mid) < TOLERANCE_DEG:
            return jd_mid

        if diff_low * diff_mid <= 0:
            jd_high    = jd_mid
            diff_high  = diff_mid
        else:
            jd_low    = jd_mid
            diff_low  = diff_mid

    jd_final = (jd_low + jd_high) / 2.0
    diff_deg = abs(_signed_angle_diff(_get_sun_sidereal_lon(jd_final), natal_sidereal_sun_lon))
    if diff_deg > TOLERANCE_DEG:
        raise RuntimeError('Convergence failed')
    return jd_final


def build_solar_return_array(birth_jd: float,
                              natal_sidereal_sun_lon: float,
                              n_years: int = 35) -> np.ndarray:
    solar_return_jds = np.zeros(n_years, dtype=np.float64)
    for y in range(1, n_years + 1):
        solar_return_jds[y - 1] = find_solar_return_jd(
            birth_jd, natal_sidereal_sun_lon, y
        )
    return solar_return_jds


def get_natal_sidereal_sun_lon(birth_jd: float) -> float:
    return _get_sun_sidereal_lon(birth_jd)


if __name__ == "__main__":
    swe.set_ephe_path(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\ephe")
    BIRTH_JD = swe.julday(1993, 1, 29, 14.5)
    natal_sun = get_natal_sidereal_sun_lon(BIRTH_JD)
    print(f"[VALIDATION] SPY Natal Sidereal Sun: {natal_sun:.6f} deg")

    sr_jds = build_solar_return_array(BIRTH_JD, natal_sun, n_years=5)
    for i, sr_jd in enumerate(sr_jds, 1):
        actual_lon = _get_sun_sidereal_lon(sr_jd)
        diff = abs(_signed_angle_diff(actual_lon, natal_sun))
        print(f"  Year {i}: JD={sr_jd:.6f}, Sun={actual_lon:.6f} deg, err={diff:.2e} deg")
        assert diff < TOLERANCE_DEG * 5, f"FAIL: Year {i} error {diff} exceeds tolerance!"
    print("[VALIDATION] varshaphala_rootfinder PASSED.")


# CRITICAL BUG FIX #17: Ensure swisseph is closed
import atexit
atexit.register(swe.close)
