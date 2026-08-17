import sys
import os
import math
import traceback
import numpy as np
import logging
from datetime import datetime

# Configure path
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base_dir, 'src'))

# Imports
from vedic_astrology.omni_vedic_fusion import (
    _safe_angular_distance, 
    _mutual_bhava, 
    _check_combustion,
    extract_omni_vedic_row
)
from core.astro_ashtakvarga import get_raw_ashtakvarga
from core.jaimini_karakas import calculate_jaimini_karakas
from core.shadbala_core import calc_shadbala
from core.astro_vargas import get_all_vargas
from core.vedha_engine import extract_vedha_features
import swisseph as swe

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("STRESS_TEST")

def run_tests():
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    failures = 0

    def assert_eq(a, b, msg):
        nonlocal failures
        try:
            if isinstance(a, float) and isinstance(b, float):
                assert math.isclose(a, b, abs_tol=1e-5), f"{msg}: {a} != {b}"
            else:
                assert a == b, f"{msg}: {a} != {b}"
        except AssertionError as e:
            logger.error(f"FAIL: {e}")
            failures += 1

    def check_no_exception(func, *args, **kwargs):
        nonlocal failures
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"EXCEPTION in {func.__name__}: {e}")
            traceback.print_exc()
            failures += 1
            return None

    # 1. ZODIACAL BOUNDARY WRAP
    logger.info("TEST 1: ZODIACAL BOUNDARY WRAP")
    test_angles = [0.0, 359.9999, 360.0, -0.001]
    for a in test_angles:
        for b in test_angles:
            dist = _safe_angular_distance(a, b)
            assert_eq(0 <= dist <= 180.0, True, f"Distance out of bounds for {a}, {b}: {dist}")
            bhava = _mutual_bhava(a, b)
            assert_eq(1 <= bhava <= 12, True, f"Bhava out of bounds for {a}, {b}: {bhava}")

    # 2. GANDANTA JUNCTION POINTS
    logger.info("TEST 2: GANDANTA JUNCTION POINTS")
    gandanta_points = [29.167, 239.167, 359.167]
    for p in gandanta_points:
        check_no_exception(get_all_vargas, p)

    # 3. ZERO-SPEED STAMBHANA
    logger.info("TEST 3: ZERO-SPEED STAMBHANA")
    shadbala_input = {
        n: {"longitude": 100.0, "speed": 0.0} 
        for n in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    }
    sb = check_no_exception(calc_shadbala, shadbala_input, 10.0, 100.0, 150.0, 2451545.0, 0.0)
    if sb:
        for p_name, p_sb in sb.items():
            assert_eq(math.isfinite(p_sb.get("total_rupas", float('nan'))), True, f"Shadbala for {p_name} is NaN/Inf due to zero speed")

    # 4. NAKSHATRA BOUNDARIES
    logger.info("TEST 4: NAKSHATRA BOUNDARIES")
    for i in range(28):
        lon = i * (360.0 / 27.0)
        vargas = check_no_exception(get_all_vargas, lon)
        if vargas is not None:
            assert_eq(len(vargas), 16, f"Vargas array length invalid at {lon}")

    # 5. PADA BOUNDARIES
    logger.info("TEST 5: PADA BOUNDARIES")
    for i in range(109):
        lon = i * (360.0 / 108.0)
        vargas = check_no_exception(get_all_vargas, lon)
        if vargas is not None:
            assert_eq(len(vargas), 16, f"Vargas array length invalid at {lon}")

    # 6. KAKSHYA BOUNDARIES
    logger.info("TEST 6: KAKSHYA BOUNDARIES")
    for i in range(97):
        lon = i * 3.75
        vargas = check_no_exception(get_all_vargas, lon)

    # 7. SIGN BOUNDARIES
    logger.info("TEST 7: SIGN BOUNDARIES")
    sign_bounds = [i * 30.0 for i in range(13)] + [i*30.0 - 0.0001 for i in range(1, 13)] + [i*30.0 + 0.0001 for i in range(12)]
    for lon in sign_bounds:
        vargas = check_no_exception(get_all_vargas, lon)

    # 8. IDENTICAL PLANETARY LONGITUDES
    logger.info("TEST 8: IDENTICAL PLANETARY LONGITUDES")
    positions = {
        n: {"longitude": 45.0, "speed": 1.0, "sign_idx": 1, "is_retrograde": False}
        for n in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    }
    combust = check_no_exception(_check_combustion, positions)
    if combust is not None:
        assert_eq(len(combust), 6, "Combustion dict length invalid")

    # Jaimini exact same longitudes
    planets_list = [
        {"planet": n, "longitude": 45.0}
        for n in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    ]
    jaimini_res = check_no_exception(calculate_jaimini_karakas, planets_list)
    if jaimini_res is not None:
        assert_eq(len(jaimini_res), 7, "Jaimini karakas didn't return 7 results for identical degrees")

    # 9. ALL PLANETS IN SAME SIGN
    logger.info("TEST 9: ALL PLANETS IN SAME SIGN")
    sign_indices = np.zeros(8, dtype=np.int32)
    bav, sav = check_no_exception(get_raw_ashtakvarga, sign_indices)
    if sav is not None:
        total_sav = np.sum(sav)
        assert_eq(total_sav, 337, f"SAV total expected 337, got {total_sav}")

    # 10. EXTREME HISTORICAL DATES
    logger.info("TEST 10: EXTREME HISTORICAL DATES")
    # 1792, 1900, 2000, 2050
    years = [1792, 1900, 2000, 2050]
    for y in years:
        jd_ut = swe.julday(y, 5, 17, 12.0)
        row = check_no_exception(extract_omni_vedic_row, jd_ut)
        if row is not None:
            assert_eq(isinstance(row, dict), True, "extract_omni_vedic_row did not return dict")
            logger.info(f"Year {y} returned {len(row)} features")
            
    if failures == 0:
        logger.info("ALL STRESS TESTS PASSED!")
        sys.exit(0)
    else:
        logger.error(f"{failures} FAILURES DETECTED.")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
