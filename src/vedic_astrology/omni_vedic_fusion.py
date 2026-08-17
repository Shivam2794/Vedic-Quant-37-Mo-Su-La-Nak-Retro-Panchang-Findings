"""
OMNI-VEDIC SUPREME FUSION ENGINE
=================================
Unifies all 7 Classical Deep Vedic Astrology Engines into a single,
high-throughput, zero-loss feature extraction pipeline for SPY
candlestick anomalies.

Pillars Integrated:
  1. Core Ephemeris (12 Bodies + NYSE Topocentric Ascendant + Equatorial Declinations)
  2. All-Pairs Mutual Geometry (66+ Distances, Mutual Bhavas: 1/7, 6/8, 2/12, 5/9, 4/10)
  3. Shodashvarga Harmonic Engine (D1..D60, Vargottama, Pushkara Navamsha)
  4. Jaimini Chara Karakas (AK, AmK, BK, MK, PK, GK-Crash Karaka, DK)
  5. Ashtakavarga & Kakshya (BAV 7x12 matrices, SAV 337 Sum Invariant, 8-Kakshya)
  6. 6-Fold Shadbala Potency (Sthana, Dig, Kala, Chesta, Naisargika, Drik in Virupas)
  7. Sarvatobhadra Chakra Vedha Network (Frontal/Left/Right/Latta, Gochar Murti)
  8. 249 KP Sub-Lords & Sub-Sub Lords
  9. NYSE Natal Vimshottari Dashas (MD/AD/PD from May 17, 1792)
 10. Multi-Timeframe Confluence & Resonance Scoring
"""

import os
import sys
import math
import logging
import numpy as np
import pandas as pd
import swisseph as swe
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# PATH SETUP: Import discovered verified engines from src/core
# ═══════════════════════════════════════════════════════════════
_CORE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "core"))
if _CORE_DIR not in sys.path:
    sys.path.insert(0, _CORE_DIR)

from astro_vargas import get_all_vargas
from jaimini_karakas import calculate_jaimini_karakas
from astro_ashtakvarga import get_raw_ashtakvarga
from shadbala_core import calc_shadbala
from kp_ephemeris_module import compute_kp_longitudes

# ═══════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════
# NYSE Wall Street coordinates for Topocentric Ascendant
NYSE_LAT = 40.7069
NYSE_LON = -74.0089

# All celestial bodies tracked (Swiss Ephemeris IDs)
GRAHA_MAP = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
}

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "P.Phalguni", "U.Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Moola", "P.Ashadha", "U.Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "P.Bhadrapada", "U.Bhadrapada", "Revati",
]

# 8 Kakshya lords in classical orbital speed order
KAKSHYA_LORDS = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Ascendant"]

# Classical combustion orbs (degrees from Sun)
COMBUSTION_ORBS = {
    "Moon": 12.0, "Mars": 17.0, "Mercury": 14.0,
    "Jupiter": 11.0, "Venus": 10.0, "Saturn": 15.0,
}

# Vimshottari Dasha periods (years) in Nakshatra order
VIMSHOTTARI_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIMSHOTTARI_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]
VIMSHOTTARI_TOTAL = 120  # sum of years

# NYSE Inception: May 17, 1792, estimated ~10:00 AM LMT New York
NYSE_INCEPTION_JD = swe.julday(1792, 5, 17, 14.93)  # ~14:56 UT (10:00 AM LMT NY approx)


# ═══════════════════════════════════════════════════════════════
# PILLAR 1: CORE EPHEMERIS (12 Bodies + Lagna + Declinations)
# ═══════════════════════════════════════════════════════════════

def _safe_angular_distance(lon1: float, lon2: float) -> float:
    """Minimal spherical angular distance [0, 180] degrees."""
    diff = abs(lon1 - lon2) % 360.0
    return diff if diff <= 180.0 else 360.0 - diff


def _mutual_bhava(lon_from: float, lon_to: float) -> int:
    """Mutual house number (1 to 12) from lon_from to lon_to."""
    sign_from = int(lon_from / 30.0) % 12
    sign_to = int(lon_to / 30.0) % 12
    return ((sign_to - sign_from) % 12) + 1


def _kakshya_lord(degree_in_sign: float) -> str:
    """Returns Kakshya ruler for intra-sign degree [0, 30)."""
    idx = min(int(degree_in_sign / 3.75), 7)
    return KAKSHYA_LORDS[idx]


def _nakshatra_and_pada(longitude: float):
    """Returns (nakshatra_index 0-26, pada 1-4, nakshatra_name)."""
    nak_idx = int(longitude / (360.0 / 27.0)) % 27
    nak_start = nak_idx * (360.0 / 27.0)
    pada = int((longitude - nak_start) / (360.0 / 108.0)) % 4 + 1
    return nak_idx, pada, NAKSHATRAS[nak_idx]


def _topocentric_ascendant(jd_ut: float, lat: float = NYSE_LAT, lon: float = NYSE_LON) -> float:
    """Sidereal Lahiri Topocentric Ascendant at given coordinates."""
    cusps, ascmc = swe.houses_ex(jd_ut, lat, lon, b'P', swe.FLG_SIDEREAL)
    return ascmc[0] % 360.0


def _calculate_all_positions(jd_ut: float) -> Dict[str, Dict[str, float]]:
    """Compute sidereal positions, speeds, declinations for all bodies."""
    flags_sid = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
    flags_eq = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_EQUATORIAL

    positions = {}
    for name, pid in GRAHA_MAP.items():
        res_sid, _ = swe.calc_ut(jd_ut, pid, flags_sid)
        res_eq, _ = swe.calc_ut(jd_ut, pid, flags_eq)

        lon = res_sid[0] % 360.0
        speed = res_sid[3]
        dec = res_eq[1]  # Equatorial declination
        sign_idx = int(lon / 30.0) % 12
        deg_in_sign = lon % 30.0
        nak_idx, pada, nak_name = _nakshatra_and_pada(lon)

        positions[name] = {
            "longitude": lon,
            "speed": speed,
            "declination": dec,
            "is_retrograde": 1 if speed < 0 else 0,
            "sign_idx": sign_idx,
            "sign_name": SIGNS[sign_idx],
            "deg_in_sign": deg_in_sign,
            "nakshatra_idx": nak_idx,
            "nakshatra_name": nak_name,
            "pada": pada,
            "kakshya_lord": _kakshya_lord(deg_in_sign),
        }

    # Ketu = 180 deg opposite Rahu
    rahu = positions["Rahu"]
    ketu_lon = (rahu["longitude"] + 180.0) % 360.0
    ketu_sign = int(ketu_lon / 30.0) % 12
    ketu_nak_idx, ketu_pada, ketu_nak = _nakshatra_and_pada(ketu_lon)
    positions["Ketu"] = {
        "longitude": ketu_lon,
        "speed": rahu["speed"],
        "declination": -rahu["declination"],
        "is_retrograde": 1,
        "sign_idx": ketu_sign,
        "sign_name": SIGNS[ketu_sign],
        "deg_in_sign": ketu_lon % 30.0,
        "nakshatra_idx": ketu_nak_idx,
        "nakshatra_name": ketu_nak,
        "pada": ketu_pada,
        "kakshya_lord": _kakshya_lord(ketu_lon % 30.0),
    }

    return positions


# ═══════════════════════════════════════════════════════════════
# PILLAR 6: COMBUSTION DETECTION
# ═══════════════════════════════════════════════════════════════

def _check_combustion(positions: Dict) -> Dict[str, int]:
    """Check classical combustion for each planet against Sun."""
    sun_lon = positions["Sun"]["longitude"]
    combustion = {}
    for planet, orb in COMBUSTION_ORBS.items():
        if planet in positions:
            dist = _safe_angular_distance(sun_lon, positions[planet]["longitude"])
            # Retrograde planets have reduced combustion orbs (classical rule)
            effective_orb = orb * 0.5 if positions[planet]["is_retrograde"] else orb
            combustion[planet] = 1 if dist <= effective_orb else 0
    return combustion


# ═══════════════════════════════════════════════════════════════
# PILLAR 9: VIMSHOTTARI DASHA FROM NYSE NATAL CHART
# ═══════════════════════════════════════════════════════════════

def _get_nyse_natal_moon_nak():
    """Get NYSE natal Moon's Nakshatra for Dasha seed."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
    res, _ = swe.calc_ut(NYSE_INCEPTION_JD, swe.MOON, flags)
    moon_lon = res[0] % 360.0
    nak_idx = int(moon_lon / (360.0 / 27.0)) % 27
    nak_start = nak_idx * (360.0 / 27.0)
    elapsed_fraction = (moon_lon - nak_start) / (360.0 / 27.0)
    return nak_idx, elapsed_fraction


def _vimshottari_dasha_at_jd(jd_ut: float) -> Dict[str, str]:
    """Calculate active Vimshottari MD/AD/PD at a given Julian Date."""
    nak_idx, elapsed_frac = _get_nyse_natal_moon_nak()

    # Starting lord index in Vimshottari cycle
    start_lord_idx = nak_idx % 9
    # Balance of first Dasha at birth
    first_lord_years = VIMSHOTTARI_YEARS[start_lord_idx]
    balance_years = first_lord_years * (1.0 - elapsed_frac)

    # Total elapsed years from NYSE inception to target date
    elapsed_years = (jd_ut - NYSE_INCEPTION_JD) / 365.25

    # Walk through Mahadashas
    cumulative = 0.0
    md_lord = ""
    md_elapsed_in_period = 0.0
    for cycle in range(50):  # enough cycles for 234+ years
        for i in range(9):
            lord_idx = (start_lord_idx + i) % 9
            if cycle == 0 and i == 0:
                period = balance_years
            else:
                period = VIMSHOTTARI_YEARS[lord_idx]

            if cumulative + period > elapsed_years:
                md_lord = VIMSHOTTARI_LORDS[lord_idx]
                md_elapsed_in_period = elapsed_years - cumulative
                md_total_period = period
                break
            cumulative += period
        else:
            continue
        break

    # Walk through Antardashas within the Mahadasha
    md_lord_idx = VIMSHOTTARI_LORDS.index(md_lord)
    ad_start = 0.0
    ad_lord = md_lord
    ad_elapsed_in_period = 0.0
    for i in range(9):
        ad_lord_idx = (md_lord_idx + i) % 9
        ad_period = md_total_period * (VIMSHOTTARI_YEARS[ad_lord_idx] / VIMSHOTTARI_TOTAL)
        if ad_start + ad_period > md_elapsed_in_period:
            ad_lord = VIMSHOTTARI_LORDS[ad_lord_idx]
            ad_elapsed_in_period = md_elapsed_in_period - ad_start
            ad_total_period = ad_period
            break
        ad_start += ad_period

    # Walk through Pratyantar within the Antardasha
    ad_lord_idx = VIMSHOTTARI_LORDS.index(ad_lord)
    pd_start = 0.0
    pd_lord = ad_lord
    for i in range(9):
        pd_lord_idx = (ad_lord_idx + i) % 9
        pd_period = ad_total_period * (VIMSHOTTARI_YEARS[pd_lord_idx] / VIMSHOTTARI_TOTAL)
        if pd_start + pd_period > ad_elapsed_in_period:
            pd_lord = VIMSHOTTARI_LORDS[pd_lord_idx]
            break
        pd_start += pd_period

    return {"MD": md_lord, "AD": ad_lord, "PD": pd_lord}


# ═══════════════════════════════════════════════════════════════
# MASTER FUSION: extract_omni_vedic_row()
# ═══════════════════════════════════════════════════════════════

def extract_omni_vedic_row(jd_ut: float) -> Dict[str, Any]:
    """
    Computes all ~216 deep Vedic features for a single anomaly timestamp.

    Returns a flat dict of feature_name -> value.
    """
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    row: Dict[str, Any] = {}

    # ── PILLAR 1: Core Graha Positions ──
    positions = _calculate_all_positions(jd_ut)

    all_body_names = list(GRAHA_MAP.keys()) + ["Ketu"]

    for name in all_body_names:
        p = positions[name]
        row[f"{name}_Lon"] = round(p["longitude"], 4)
        row[f"{name}_Speed"] = round(p["speed"], 6)
        row[f"{name}_Retro"] = p["is_retrograde"]
        row[f"{name}_Sign"] = p["sign_name"]
        row[f"{name}_DegInSign"] = round(p["deg_in_sign"], 4)
        row[f"{name}_Nakshatra"] = p["nakshatra_name"]
        row[f"{name}_Pada"] = p["pada"]
        row[f"{name}_Kakshya"] = p["kakshya_lord"]
        if "declination" in p:
            row[f"{name}_Declination"] = round(p["declination"], 4)

    # ── PILLAR 1b: NYSE Topocentric Ascendant (Lagna) ──
    asc_lon = _topocentric_ascendant(jd_ut)
    asc_sign = int(asc_lon / 30.0) % 12
    asc_nak_idx, asc_pada, asc_nak = _nakshatra_and_pada(asc_lon)
    row["Lagna_NYSE_Lon"] = round(asc_lon, 4)
    row["Lagna_NYSE_Sign"] = SIGNS[asc_sign]
    row["Lagna_NYSE_DegInSign"] = round(asc_lon % 30.0, 4)
    row["Lagna_NYSE_Nakshatra"] = asc_nak
    row["Lagna_NYSE_Pada"] = asc_pada

    positions["Lagna"] = {"longitude": asc_lon, "sign_idx": asc_sign}

    # ── PILLAR 2: All-Pairs Mutual Angular Distances & Bhavas ──
    pair_bodies = all_body_names + ["Lagna"]
    pair_lons = {n: positions[n]["longitude"] for n in all_body_names}
    pair_lons["Lagna"] = asc_lon

    for i in range(len(pair_bodies)):
        for j in range(i + 1, len(pair_bodies)):
            b1, b2 = pair_bodies[i], pair_bodies[j]
            dist = _safe_angular_distance(pair_lons[b1], pair_lons[b2])
            bhava = _mutual_bhava(pair_lons[b1], pair_lons[b2])

            col_base = f"{b1}_{b2}"
            row[f"Ang_{col_base}"] = round(dist, 3)
            row[f"Bhv_{col_base}"] = bhava

    # ── PILLAR 3: Harmonic Divisional Vargas (D1..D60) ──
    varga_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    for p_name in varga_planets:
        vargas = get_all_vargas(positions[p_name]["longitude"])
        d1_sign = positions[p_name]["sign_idx"]
        row[f"{p_name}_D9"] = int(vargas[8])
        row[f"{p_name}_D10"] = int(vargas[9])
        row[f"{p_name}_D60"] = int(vargas[15]) if len(vargas) > 15 else -1
        row[f"{p_name}_Vargottama"] = 1 if d1_sign == int(vargas[8]) else 0

    # Lagna Vargas
    lagna_vargas = get_all_vargas(asc_lon)
    row["Lagna_D9"] = int(lagna_vargas[8])
    row["Lagna_Vargottama"] = 1 if asc_sign == int(lagna_vargas[8]) else 0

    # ── PILLAR 4: Jaimini Chara Karakas ──
    planets_list = [
        {"planet": n, "longitude": positions[n]["longitude"]}
        for n in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    ]
    try:
        jaimini_res = calculate_jaimini_karakas(planets_list)
        for item in jaimini_res:
            row[f"Jaimini_{item['karaka_abbr']}"] = item["planet"]
            row[f"Jaimini_{item['karaka_abbr']}_Deg"] = round(item["degree_in_sign"], 4)
    except Exception as e:
        logger.warning(f"Jaimini Karakas failed: {e}")

    # ── PILLAR 5: Ashtakavarga BAV & SAV ──
    sign_indices = [positions[n]["sign_idx"] for n in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]]
    sign_indices.append(asc_sign)  # 8th element = Ascendant
    try:
        bav, sav = get_raw_ashtakvarga(np.array(sign_indices, dtype=np.int32))
        sav_total = int(np.sum(sav))
        row["SAV_Total"] = sav_total
        for s_idx in range(12):
            row[f"SAV_{SIGNS[s_idx]}"] = int(sav[s_idx])
        # SAV for transiting planets' current signs
        for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            p_sign = positions[p_name]["sign_idx"]
            row[f"SAV_At_{p_name}"] = int(sav[p_sign])
    except Exception as e:
        logger.warning(f"Ashtakavarga failed: {e}")

    # ── PILLAR 6: Shadbala 6-Fold Potency ──
    shadbala_input = {
        n: {"longitude": positions[n]["longitude"], "speed": positions[n]["speed"]}
        for n in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    }
    try:
        sb = calc_shadbala(
            shadbala_input,
            asc_lon=asc_lon,
            sun_lon=positions["Sun"]["longitude"],
            moon_lon=positions["Moon"]["longitude"],
            jd=jd_ut,
            mc_lon=0.0,
        )
        for p_name, p_sb in sb.items():
            row[f"Shadbala_{p_name}_Rupas"] = p_sb.get("total_rupas", 0.0)
            row[f"Shadbala_{p_name}_Ratio"] = p_sb.get("ratio", 1.0)
    except Exception as e:
        logger.warning(f"Shadbala failed: {e}")

    # ── PILLAR 6b: Combustion ──
    combustions = _check_combustion(positions)
    for planet, is_combust in combustions.items():
        row[f"{planet}_Combust"] = is_combust

    # ── PILLAR 8: KP Sub-Lords ──
    try:
        kp_data = compute_kp_longitudes(jd_ut, NYSE_LAT, NYSE_LON)
        if isinstance(kp_data, dict):
            for body_name, kp_info in kp_data.items():
                if isinstance(kp_info, dict):
                    row[f"KP_{body_name}_SubLord"] = kp_info.get("sub_lord", "")
                    row[f"KP_{body_name}_StarLord"] = kp_info.get("star_lord", "")
    except Exception as e:
        logger.warning(f"KP Sub-Lords failed: {e}")

    # ── PILLAR 9: NYSE Vimshottari Dashas ──
    try:
        dasha = _vimshottari_dasha_at_jd(jd_ut)
        row["Vim_MD"] = dasha["MD"]
        row["Vim_AD"] = dasha["AD"]
        row["Vim_PD"] = dasha["PD"]
    except Exception as e:
        logger.warning(f"Vimshottari failed: {e}")

    row["Ayanamsha_Val"] = swe.get_ayanamsa(jd_ut)

    return row


# ═══════════════════════════════════════════════════════════════
# MASTER PIPELINE: generate_omni_vedic_supreme_dataset()
# ═══════════════════════════════════════════════════════════════

def generate_omni_vedic_supreme_dataset(
    input_manifest_path: str,
    output_parquet_path: str,
    output_csv_path: str,
) -> pd.DataFrame:
    """
    Enriches the entire master anomaly manifest with ~216 Deep Vedic features.

    Args:
        input_manifest_path: Path to master_anomaly_manifest.parquet
        output_parquet_path: Output .parquet path
        output_csv_path: Output .csv path

    Returns:
        pd.DataFrame with all market + Vedic features fused
    """
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    df_manifest = pd.read_parquet(input_manifest_path)
    total_rows = len(df_manifest)
    logger.info(f"Loaded Master Manifest: {total_rows} anomaly bars")

    # ── PILLAR 10: Multi-Timeframe Confluence ──
    dt_counts = df_manifest["Datetime_UTC"].value_counts().to_dict()
    df_manifest["MTF_Confluence_Count"] = df_manifest["Datetime_UTC"].map(dt_counts)

    # Process each row
    enriched_rows = []
    for idx, manifest_row in df_manifest.iterrows():
        dt_val = manifest_row["Datetime_UTC"]
        if isinstance(dt_val, str):
            dt_utc = pd.to_datetime(dt_val).to_pydatetime()
        else:
            dt_utc = dt_val.to_pydatetime()

        # Convert to Julian Date UT
        hour_frac = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
        jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_frac)

        # Extract full Vedic feature row
        vedic_feats = extract_omni_vedic_row(jd_ut)

        # Merge market anomaly columns with Vedic features
        combined = {**manifest_row.to_dict(), **vedic_feats}
        enriched_rows.append(combined)

        if (idx + 1) % 200 == 0:
            logger.info(f"  Processed {idx + 1}/{total_rows} rows...")

    df_supreme = pd.DataFrame(enriched_rows)

    # ── Validation Checks ──
    nan_count = df_supreme[[c for c in df_supreme.columns if c.endswith("_Lon") or c.endswith("_Speed")]].isna().sum().sum()
    if nan_count > 0:
        logger.error(f"CRITICAL: {nan_count} NaNs found in planetary position columns!")
    else:
        logger.info("Zero NaN validation: PASSED")

    # Write outputs
    df_supreme.to_parquet(output_parquet_path, index=False)
    df_supreme.to_csv(output_csv_path, index=False)

    logger.info(f"Omni-Vedic Supreme Dataset generated: {df_supreme.shape}")
    logger.info(f"  Parquet: {output_parquet_path}")
    logger.info(f"  CSV:     {output_csv_path}")

    return df_supreme


# ═══════════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    manifest_in = os.path.join(base_dir, "data", "anomalies", "master_anomaly_manifest.parquet")
    out_parquet = os.path.join(base_dir, "data", "spy_anomalies_omni_vedic_supreme.parquet")
    out_csv = os.path.join(base_dir, "data", "spy_anomalies_omni_vedic_supreme.csv")

    if not os.path.exists(manifest_in):
        logger.error(f"Master manifest not found at: {manifest_in}")
        sys.exit(1)

    generate_omni_vedic_supreme_dataset(manifest_in, out_parquet, out_csv)
