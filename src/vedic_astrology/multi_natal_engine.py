"""
CANONICAL MULTI-NATAL ENTITY ENGINE
===================================
Institutional-grade, bit-exact astronomical calculation of 4 core financial
and mundane natal anchor charts:
1. SPY ETF Inception (January 29, 1993, 09:30:00 AM EST, New York, NY)
2. USA Declaration / Sibly Chart (July 4, 1776, 17:10:00 LMT, Philadelphia, PA)
3. Federal Reserve Act (December 23, 1913, 18:02:00 EST, Washington, D.C.)
4. NYSE Buttonwood Agreement (May 17, 1792, 10:00:00 LMT, New York, NY)

Computes:
- Canonical Sidereal Lahiri natal planetary longitudes, signs, nakshatras, and Lagna.
- Exact sub-second Vimshottari Mahadasha / Antardasha / Pratyantardasha (MD/AD/PD).
- Transit-to-Natal Gochar Bhavas (House relationships relative to Natal Lagna and Natal Moon).
- Active Sade-Sati, Kantaka Shani, and Ashtama Shani status against each entity's Natal Moon.
"""

import math
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, List, Optional
import swisseph as swe

# ─── VEDIC CONSTANTS ──────────────────────────────────────────────────────────
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "P.Phalguni", "U.Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Moola", "P.Ashadha", "U.Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "P.Bhadrapada", "U.Bhadrapada", "Revati"
]

DASHA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]

DASHA_YEARS = {
    "Ketu": 7.0,
    "Venus": 20.0,
    "Sun": 6.0,
    "Moon": 10.0,
    "Mars": 7.0,
    "Rahu": 18.0,
    "Jupiter": 16.0,
    "Saturn": 19.0,
    "Mercury": 17.0
}

TOTAL_VIMSHOTTARI_CYCLE = 120.0  # Solar years
NAKSHATRA_SPAN_DEG = 360.0 / 27.0  # 13°20' = 13.333333333333334 degrees
SIDEREAL_YEAR = 365.25636042  # Days in sidereal year (Trap P2.9 fix)

# ─── 4 CANONICAL NATAL CHART SPECIFICATIONS ──────────────────────────────────
# 1. SPY ETF First Trade: 1993-01-29 09:30:00 EST (UTC = 14:30:00)
#    Coordinates: AMEX / Wall Street (40.7069° N, 74.0089° W)
SPY_BIRTH = {
    "name": "SPY",
    "year": 1993, "month": 1, "day": 29,
    "hour_utc": 14.50,  # 09:30 AM EST = 14:30 UTC
    "lat": 40.7069, "lon": -74.0089,
    "description": "SPY ETF Inception & First Trade (AMEX)"
}

# 2. USA Declaration (Sibly Chart): 1776-07-04 17:10:00 LMT (UTC = 22:10:40)
#    Coordinates: Independence Hall, Philadelphia, PA (39.9526° N, 75.1652° W)
#    LMT offset = -75.1652 / 15 = -5.01101 hours -> 17.16667 + 5.01101 = 22.17768 UTC
USA_BIRTH = {
    "name": "USA",
    "year": 1776, "month": 7, "day": 4,
    "hour_utc": 22.17768,
    "lat": 39.9526, "lon": -75.1652,
    "description": "USA Independence Declaration (Sibly Chart)"
}

# 3. Federal Reserve Act: 1913-12-23 18:02:00 EST (UTC = 23:02:00)
#    Coordinates: White House, Washington D.C. (38.8951° N, 77.0364° W)
FED_BIRTH = {
    "name": "Fed",
    "year": 1913, "month": 12, "day": 23,
    "hour_utc": 23.03333,  # 18:02 EST = 23:02 UTC
    "lat": 38.8951, "lon": -77.0364,
    "description": "Federal Reserve Act Signed (Woodrow Wilson)"
}

# 4. NYSE Buttonwood Agreement: 1792-05-17 10:00:00 LMT (UTC = 14:56:02)
#    Coordinates: 68 Wall Street, New York, NY (40.7069° N, 74.0089° W)
#    LMT offset = -74.0089 / 15 = -4.93393 hours -> 10.0 + 4.93393 = 14.93393 UTC
NYSE_BIRTH = {
    "name": "NYSE",
    "year": 1792, "month": 5, "day": 17,
    "hour_utc": 14.93393,
    "lat": 40.7069, "lon": -74.0089,
    "description": "NYSE Buttonwood Agreement (Wall Street)"
}

NATAL_ENTITIES = [SPY_BIRTH, USA_BIRTH, FED_BIRTH, NYSE_BIRTH]


# ─── CANONICAL CALCULATION FUNCTIONS ─────────────────────────────────────────

def calculate_natal_chart(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Computes exact Sidereal Lahiri planetary longitudes and Lagna for a natal specification."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd_ut = swe.julday(spec["year"], spec["month"], spec["day"], spec["hour_utc"])
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL

    bodies = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE
    }

    positions = {}
    for name, pid in bodies.items():
        res, _ = swe.calc_ut(jd_ut, pid, flags)
        lon = res[0] % 360.0
        sign_idx = int(lon / 30.0) % 12
        nak_idx = int(lon / NAKSHATRA_SPAN_DEG) % 27
        positions[name] = {
            "longitude": lon,
            "sign_idx": sign_idx,
            "sign": SIGNS[sign_idx],
            "nakshatra_idx": nak_idx,
            "nakshatra": NAKSHATRAS[nak_idx],
            "deg_in_sign": lon % 30.0,
        }

    # Ketu = 180° opposite Rahu
    ketu_lon = (positions["Rahu"]["longitude"] + 180.0) % 360.0
    ketu_sign = int(ketu_lon / 30.0) % 12
    ketu_nak = int(ketu_lon / NAKSHATRA_SPAN_DEG) % 27
    positions["Ketu"] = {
        "longitude": ketu_lon,
        "sign_idx": ketu_sign,
        "sign": SIGNS[ketu_sign],
        "nakshatra_idx": ketu_nak,
        "nakshatra": NAKSHATRAS[ketu_nak],
        "deg_in_sign": ketu_lon % 30.0,
    }

    # Topocentric Lagna (Ascendant)
    cusps, ascmc = swe.houses_ex(jd_ut, spec["lat"], spec["lon"], b'P', swe.FLG_SIDEREAL)
    asc_lon = ascmc[0] % 360.0
    asc_sign = int(asc_lon / 30.0) % 12
    asc_nak = int(asc_lon / NAKSHATRA_SPAN_DEG) % 27

    positions["Lagna"] = {
        "longitude": asc_lon,
        "sign_idx": asc_sign,
        "sign": SIGNS[asc_sign],
        "nakshatra_idx": asc_nak,
        "nakshatra": NAKSHATRAS[asc_nak],
        "deg_in_sign": asc_lon % 30.0,
    }

    return {
        "entity": spec["name"],
        "jd_ut": jd_ut,
        "spec": spec,
        "positions": positions,
        "moon_longitude": positions["Moon"]["longitude"],
        "moon_sign_idx": positions["Moon"]["sign_idx"],
        "moon_nakshatra_idx": positions["Moon"]["nakshatra_idx"],
        "lagna_sign_idx": positions["Lagna"]["sign_idx"],
    }


# Precompute canonical natal charts at module import time
CACHED_NATAL_CHARTS = {
    spec["name"]: calculate_natal_chart(spec) for spec in NATAL_ENTITIES
}


def calculate_vimshottari_dasha(natal_chart: Dict[str, Any], target_jd_ut: float) -> Dict[str, str]:
    """
    Computes exact fractional Vimshottari Mahadasha (MD), Antardasha (AD),
    and Pratyantardasha (PD) for a target Julian Date based on natal Moon longitude.
    """
    birth_jd = natal_chart["jd_ut"]
    if target_jd_ut < birth_jd:
        return {"MD": "PreBirth", "AD": "PreBirth", "PD": "PreBirth"}

    moon_lon = natal_chart["moon_longitude"]
    nak_idx = int(moon_lon / NAKSHATRA_SPAN_DEG) % 27
    start_lord_idx = nak_idx % 9  # Dasha lord sequence aligns with Nakshatras 0..26 mod 9

    deg_in_nak = moon_lon % NAKSHATRA_SPAN_DEG
    elapsed_frac = deg_in_nak / NAKSHATRA_SPAN_DEG
    remaining_frac = 1.0 - elapsed_frac

    birth_lord = DASHA_LORDS[start_lord_idx]
    birth_lord_total_years = DASHA_YEARS[birth_lord]
    balance_years = remaining_frac * birth_lord_total_years

    # Elapsed sidereal years between birth and target date
    elapsed_years = (target_jd_ut - birth_jd) / SIDEREAL_YEAR

    # 1. Determine Mahadasha (MD)
    current_md_lord = birth_lord
    current_md_years = birth_lord_total_years
    md_start_elapsed_years = 0.0
    md_end_elapsed_years = balance_years

    if elapsed_years < balance_years:
        # Still in the birth dasha
        time_into_md = (birth_lord_total_years - balance_years) + elapsed_years
    else:
        # Walk forward through subsequent dasha lords in 120-year cycle
        curr_elapsed = balance_years
        lord_idx = (start_lord_idx + 1) % 9
        
        while True:
            lord_name = DASHA_LORDS[lord_idx]
            lord_span = DASHA_YEARS[lord_name]
            if elapsed_years < curr_elapsed + lord_span:
                current_md_lord = lord_name
                current_md_years = lord_span
                md_start_elapsed_years = curr_elapsed
                md_end_elapsed_years = curr_elapsed + lord_span
                time_into_md = elapsed_years - curr_elapsed
                break
            curr_elapsed += lord_span
            lord_idx = (lord_idx + 1) % 9

    # 2. Determine Antardasha (AD) within MD
    # Antardasha sequence starts from the Mahadasha lord itself
    md_lord_idx = DASHA_LORDS.index(current_md_lord)
    current_ad_lord = current_md_lord
    current_ad_years = 0.0
    ad_start_time = 0.0
    time_into_ad = 0.0

    accum_ad_time = 0.0
    for ad_step in range(9):
        ad_idx = (md_lord_idx + ad_step) % 9
        ad_name = DASHA_LORDS[ad_idx]
        ad_span_years = (current_md_years * DASHA_YEARS[ad_name]) / TOTAL_VIMSHOTTARI_CYCLE

        if time_into_md < accum_ad_time + ad_span_years or ad_step == 8:
            current_ad_lord = ad_name
            current_ad_years = ad_span_years
            ad_start_time = accum_ad_time
            time_into_ad = time_into_md - accum_ad_time
            break
        accum_ad_time += ad_span_years

    # 3. Determine Pratyantardasha (PD) within AD
    # Pratyantardasha sequence starts from the Antardasha lord itself
    ad_lord_idx = DASHA_LORDS.index(current_ad_lord)
    current_pd_lord = current_ad_lord

    accum_pd_time = 0.0
    for pd_step in range(9):
        pd_idx = (ad_lord_idx + pd_step) % 9
        pd_name = DASHA_LORDS[pd_idx]
        pd_span_years = (current_ad_years * DASHA_YEARS[pd_name]) / TOTAL_VIMSHOTTARI_CYCLE

        if time_into_ad < accum_pd_time + pd_span_years or pd_step == 8:
            current_pd_lord = pd_name
            break
        accum_pd_time += pd_span_years

    return {
        "MD": current_md_lord,
        "AD": current_ad_lord,
        "PD": current_pd_lord
    }


def calculate_gochar_bhavas(transiting_signs: Dict[str, int], natal_chart: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes transit-to-natal house positions (1 to 12) for core transiting planets
    relative to the natal Moon sign (Chandra Lagna) and natal Ascendant (Lagna).
    """
    n_moon_sign = natal_chart["moon_sign_idx"]
    n_lagna_sign = natal_chart["lagna_sign_idx"]
    entity_prefix = natal_chart["entity"]

    results = {}
    for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        if p_name in transiting_signs:
            t_sign = transiting_signs[p_name]
            # House relative to Natal Moon (Chandra Lagna)
            bhv_moon = ((t_sign - n_moon_sign) % 12) + 1
            # House relative to Natal Lagna (Ascendant)
            bhv_lagna = ((t_sign - n_lagna_sign) % 12) + 1
            results[f"{entity_prefix}_Gochar_{p_name}_to_Moon_Bhv"] = bhv_moon
            results[f"{entity_prefix}_Gochar_{p_name}_to_Lagna_Bhv"] = bhv_lagna

    # Sade-Sati Check: Saturn transiting 12th, 1st, or 2nd from Natal Moon
    if "Saturn" in transiting_signs:
        sat_sign = transiting_signs["Saturn"]
        sat_rel_moon = ((sat_sign - n_moon_sign) % 12) + 1
        results[f"{entity_prefix}_Is_Sade_Sati"] = 1 if sat_rel_moon in [12, 1, 2] else 0
        results[f"{entity_prefix}_Is_Ashtama_Shani"] = 1 if sat_rel_moon == 8 else 0
        results[f"{entity_prefix}_Is_Kantaka_Shani"] = 1 if sat_rel_moon in [4, 7, 10] else 0

    # Jupiter Guru Gochar Check: Benefic houses (2, 5, 7, 9, 11) from Natal Moon
    if "Jupiter" in transiting_signs:
        jup_sign = transiting_signs["Jupiter"]
        jup_rel_moon = ((jup_sign - n_moon_sign) % 12) + 1
        results[f"{entity_prefix}_Is_Guru_Gochar_Benefic"] = 1 if jup_rel_moon in [2, 5, 7, 9, 11] else 0

    return results


def extract_all_multi_natal_features(target_jd_ut: float, transiting_signs: Dict[str, int]) -> Dict[str, Any]:
    """
    Computes all multi-natal Dasha, Gochar Bhava, and Sade-Sati features across
    all 4 canonical entities (SPY, USA, Fed, NYSE) for a single target timestamp.
    """
    multi_natal_row = {}

    for entity_name, natal_chart in CACHED_NATAL_CHARTS.items():
        # 1. Exact Vimshottari Dashas (MD / AD / PD)
        dashas = calculate_vimshottari_dasha(natal_chart, target_jd_ut)
        multi_natal_row[f"{entity_name}_Vim_MD"] = dashas["MD"]
        multi_natal_row[f"{entity_name}_Vim_AD"] = dashas["AD"]
        multi_natal_row[f"{entity_name}_Vim_PD"] = dashas["PD"]

        # 2. Transit-to-Natal Gochar House Relationships
        gochar_feats = calculate_gochar_bhavas(transiting_signs, natal_chart)
        multi_natal_row.update(gochar_feats)

    # Multi-Entity Sade-Sati Crisis Confluence (Count of charts simultaneously under Sade-Sati)
    sade_sati_count = sum(
        multi_natal_row.get(f"{e}_Is_Sade_Sati", 0) for e in ["SPY", "USA", "Fed", "NYSE"]
    )
    multi_natal_row["Multi_Entity_Sade_Sati_Count"] = sade_sati_count

    return multi_natal_row
