"""
Parashari Drishti (Planetary Aspects) & Astangata (Combustion) Engine.

Calculates:
1. Parashari Drishti:
   - Full sign-based and continuous longitudinal aspects (Drishti Sphuta):
     * All Grahas cast full 7th aspect (180° opposition / 6 signs forward).
     * Mars (Mangala) special aspects: 4th (90° / 3 signs forward), 7th (180°), 8th (210° / 7 signs forward).
     * Jupiter (Guru) special aspects: 5th (120° / 4 signs forward), 7th (180°), 9th (240° / 8 signs forward).
     * Saturn (Shani) special aspects: 3rd (60° / 2 signs forward), 7th (180°), 10th (270° / 9 signs forward).
     * Rahu / Ketu aspects: 5th (120°), 7th (180°), 9th (240°).
   - Specific aspect flags: Mars_Drishti_On_Moon, Saturn_Drishti_On_Moon, Jupiter_Drishti_On_Moon, Rahu_Drishti_On_Moon.
   - Continuous aspect scores (0.0 to 1.0) with customizable angular orb.

2. Astangata (Planetary Combustion):
   - Classical angular separation thresholds from the Sun:
     * Moon: 12.0°
     * Mars: 17.0°
     * Mercury: 14.0° (Direct) / 12.0° (Retrograde)
     * Jupiter: 11.0°
     * Venus: 10.0° (Direct) / 8.0° (Retrograde)
     * Saturn: 15.0°
   - Deep combustion / Cazimi detection (< 1.0° separation).
   - Summary string column Combust_Planets and individual boolean flags.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

# Classical Parashari House Aspects (forward sign distance 0-indexed: 6 = 7th house)
PARASHARI_HOUSE_ASPECTS: Dict[str, List[int]] = {
    "Sun": [6],               # 7th
    "Moon": [6],              # 7th
    "Mars": [3, 6, 7],        # 4th, 7th, 8th
    "Mercury": [6],           # 7th
    "Jupiter": [4, 6, 8],     # 5th, 7th, 9th
    "Venus": [6],             # 7th
    "Saturn": [2, 6, 9],      # 3rd, 7th, 10th
    "Rahu": [4, 6, 8],        # 5th, 7th, 9th
    "Ketu": [4, 6, 8],        # 5th, 7th, 9th
}

# Longitudinal Angles corresponding to classical aspects
PARASHARI_EXACT_ANGLES: Dict[str, List[float]] = {
    "Sun": [180.0],
    "Moon": [180.0],
    "Mars": [90.0, 180.0, 210.0],
    "Mercury": [180.0],
    "Jupiter": [120.0, 180.0, 240.0],
    "Venus": [180.0],
    "Saturn": [60.0, 180.0, 270.0],
    "Rahu": [120.0, 180.0, 240.0],
    "Ketu": [120.0, 180.0, 240.0],
}

# Classical Combustion Orbs (in degrees)
COMBUSTION_ORBS_DIRECT: Dict[str, float] = {
    "Moon": 12.0,
    "Mars": 17.0,
    "Mercury": 14.0,
    "Jupiter": 11.0,
    "Venus": 10.0,
    "Saturn": 15.0,
}

COMBUSTION_ORBS_RETROGRADE: Dict[str, float] = {
    "Moon": 12.0,
    "Mars": 17.0,
    "Mercury": 12.0,
    "Jupiter": 11.0,
    "Venus": 8.0,
    "Saturn": 15.0,
}


def angular_separation(lon1: float, lon2: float) -> float:
    """
    Computes the shortest angular separation between two longitudes on a 360° circle.
    """
    diff = abs(float(lon1) - float(lon2)) % 360.0
    return min(diff, 360.0 - diff)


def angular_separation_batch(
    lons1: Union[np.ndarray, pd.Series, List[float]],
    lons2: Union[np.ndarray, pd.Series, List[float]],
) -> np.ndarray:
    """
    Vectorized shortest angular separation between two arrays of longitudes.
    """
    arr1 = np.asarray(lons1, dtype=np.float64) % 360.0
    arr2 = np.asarray(lons2, dtype=np.float64) % 360.0
    diff = np.abs(arr1 - arr2) % 360.0
    return np.minimum(diff, 360.0 - diff)


def is_rasi_aspect(source_lon: float, target_lon: float, planet_name: str) -> bool:
    """
    Determines if source planet casts a full Parashari sign-based aspect on target planet.
    """
    source_sign = int(np.floor((float(source_lon) % 360.0) / 30.0))
    target_sign = int(np.floor((float(target_lon) % 360.0) / 30.0))
    sign_diff = (target_sign - source_sign) % 12
    valid_aspects = PARASHARI_HOUSE_ASPECTS.get(planet_name, [6])
    return sign_diff in valid_aspects


def is_rasi_aspect_batch(
    source_lons: Union[np.ndarray, pd.Series, List[float]],
    target_lons: Union[np.ndarray, pd.Series, List[float]],
    planet_name: str,
) -> np.ndarray:
    """
    Vectorized Rasi-based Parashari aspect calculation between two arrays of longitudes.
    """
    s_arr = np.asarray(source_lons, dtype=np.float64) % 360.0
    t_arr = np.asarray(target_lons, dtype=np.float64) % 360.0
    s_sign = (np.floor(s_arr / 30.0).astype(int)) % 12
    t_sign = (np.floor(t_arr / 30.0).astype(int)) % 12
    sign_diff = (t_sign - s_sign) % 12
    valid_aspects = PARASHARI_HOUSE_ASPECTS.get(planet_name, [6])
    return np.isin(sign_diff, valid_aspects)


def calculate_aspect_score(
    source_lon: float,
    target_lon: float,
    planet_name: str,
    orb_deg: float = 12.0,
) -> float:
    """
    Calculates the continuous Parashari aspect strength score in [0.0, 1.0].
    """
    s_lon = float(source_lon) % 360.0
    t_lon = float(target_lon) % 360.0
    forward_dist = (t_lon - s_lon) % 360.0

    target_angles = PARASHARI_EXACT_ANGLES.get(planet_name, [180.0])
    max_score = 0.0

    for angle in target_angles:
        diff = abs(forward_dist - angle)
        diff = min(diff, 360.0 - diff)
        if diff <= orb_deg:
            score = 1.0 - (diff / orb_deg)
            if score > max_score:
                max_score = score

    return float(max_score)


def calculate_aspect_score_batch(
    source_lons: Union[np.ndarray, pd.Series, List[float]],
    target_lons: Union[np.ndarray, pd.Series, List[float]],
    planet_name: str,
    orb_deg: float = 12.0,
) -> np.ndarray:
    """
    Vectorized continuous Parashari aspect score calculation.
    """
    s_arr = np.asarray(source_lons, dtype=np.float64) % 360.0
    t_arr = np.asarray(target_lons, dtype=np.float64) % 360.0
    forward_dist = (t_arr - s_arr) % 360.0

    target_angles = PARASHARI_EXACT_ANGLES.get(planet_name, [180.0])
    scores = np.zeros(len(s_arr), dtype=np.float64)

    for angle in target_angles:
        diff = np.abs(forward_dist - angle)
        diff = np.minimum(diff, 360.0 - diff)
        angle_scores = np.maximum(0.0, 1.0 - (diff / orb_deg))
        scores = np.maximum(scores, angle_scores)

    return scores


def check_combustion(
    sun_lon: float,
    planet_lon: float,
    planet_name: str,
    is_retrograde: bool = False,
) -> Tuple[bool, float, bool]:
    """
    Checks if a planet is in combustion (Astangata) and if it is in Cazimi (deep combustion).

    Parameters
    ----------
    sun_lon : float
        Sun sidereal longitude.
    planet_lon : float
        Planet sidereal longitude.
    planet_name : str
        Name of planet ('Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn').
    is_retrograde : bool
        Whether the planet is in retrograde motion.

    Returns
    -------
    Tuple[bool, float, bool]
        (is_combust, separation_degrees, is_cazimi)
    """
    if planet_name in ("Rahu", "Ketu", "Sun"):
        return False, 0.0, False

    sep = angular_separation(sun_lon, planet_lon)
    orb = (
        COMBUSTION_ORBS_RETROGRADE.get(planet_name, 15.0)
        if is_retrograde
        else COMBUSTION_ORBS_DIRECT.get(planet_name, 15.0)
    )

    is_combust = sep <= orb
    is_cazimi = sep <= 1.0  # Deep combustion / heart of the Sun

    return bool(is_combust), float(sep), bool(is_cazimi)


def calculate_aspects_and_combustion_batch(
    df_grahas: pd.DataFrame,
    orb_deg: float = 12.0,
) -> pd.DataFrame:
    """
    Vectorized computation of all Parashari aspects and combustion states for a batch of Graha positions.

    Parameters
    ----------
    df_grahas : pd.DataFrame
        DataFrame containing Graha longitudes and retrograde columns from ephemeris.py.
    orb_deg : float
        Orb in degrees for continuous aspect score calculation.

    Returns
    -------
    pd.DataFrame
        DataFrame with full aspects and combustion columns matching project specification.
    """
    n = len(df_grahas)
    sun_lon = df_grahas["Sun_Lon"].to_numpy()
    moon_lon = df_grahas["Moon_Lon"].to_numpy()
    mars_lon = df_grahas["Mars_Lon"].to_numpy()
    mercury_lon = df_grahas["Mercury_Lon"].to_numpy()
    jupiter_lon = df_grahas["Jupiter_Lon"].to_numpy()
    venus_lon = df_grahas["Venus_Lon"].to_numpy()
    saturn_lon = df_grahas["Saturn_Lon"].to_numpy()
    rahu_lon = df_grahas["Rahu_Lon"].to_numpy()

    # 1. Parashari Drishti on Moon (Discrete Rasi aspect)
    mars_drishti_on_moon = is_rasi_aspect_batch(mars_lon, moon_lon, "Mars")
    saturn_drishti_on_moon = is_rasi_aspect_batch(saturn_lon, moon_lon, "Saturn")
    jupiter_drishti_on_moon = is_rasi_aspect_batch(jupiter_lon, moon_lon, "Jupiter")
    rahu_drishti_on_moon = is_rasi_aspect_batch(rahu_lon, moon_lon, "Rahu")

    # Continuous Aspect Scores on Moon
    mars_drishti_score = calculate_aspect_score_batch(mars_lon, moon_lon, "Mars", orb_deg)
    saturn_drishti_score = calculate_aspect_score_batch(saturn_lon, moon_lon, "Saturn", orb_deg)
    jupiter_drishti_score = calculate_aspect_score_batch(jupiter_lon, moon_lon, "Jupiter", orb_deg)

    # 2. Planetary Combustion (Astangata)
    moon_sep = angular_separation_batch(sun_lon, moon_lon)
    mars_sep = angular_separation_batch(sun_lon, mars_lon)
    mercury_sep = angular_separation_batch(sun_lon, mercury_lon)
    jupiter_sep = angular_separation_batch(sun_lon, jupiter_lon)
    venus_sep = angular_separation_batch(sun_lon, venus_lon)
    saturn_sep = angular_separation_batch(sun_lon, saturn_lon)

    mercury_retro = df_grahas["Mercury_Retrograde"].to_numpy()
    venus_retro = df_grahas["Venus_Retrograde"].to_numpy()

    mercury_orb = np.where(mercury_retro, COMBUSTION_ORBS_RETROGRADE["Mercury"], COMBUSTION_ORBS_DIRECT["Mercury"])
    venus_orb = np.where(venus_retro, COMBUSTION_ORBS_RETROGRADE["Venus"], COMBUSTION_ORBS_DIRECT["Venus"])

    moon_combust = moon_sep <= COMBUSTION_ORBS_DIRECT["Moon"]
    mars_combust = mars_sep <= COMBUSTION_ORBS_DIRECT["Mars"]
    mercury_combust = mercury_sep <= mercury_orb
    jupiter_combust = jupiter_sep <= COMBUSTION_ORBS_DIRECT["Jupiter"]
    venus_combust = venus_sep <= venus_orb
    saturn_combust = saturn_sep <= COMBUSTION_ORBS_DIRECT["Saturn"]

    # Build Combust_Planets summary strings
    combust_strings: List[str] = []
    combust_counts = np.zeros(n, dtype=int)

    for i in range(n):
        c_list = []
        if moon_combust[i]:
            c_list.append("Moon")
        if mars_combust[i]:
            c_list.append("Mars")
        if mercury_combust[i]:
            c_list.append("Mercury")
        if jupiter_combust[i]:
            c_list.append("Jupiter")
        if venus_combust[i]:
            c_list.append("Venus")
        if saturn_combust[i]:
            c_list.append("Saturn")

        combust_counts[i] = len(c_list)
        combust_strings.append(", ".join(c_list) if c_list else "NONE")

    return pd.DataFrame({
        # Parashari Drishti
        "Mars_Drishti_On_Moon": mars_drishti_on_moon,
        "Saturn_Drishti_On_Moon": saturn_drishti_on_moon,
        "Jupiter_Drishti_On_Moon": jupiter_drishti_on_moon,
        "Rahu_Drishti_On_Moon": rahu_drishti_on_moon,
        "Mars_Drishti_Score": mars_drishti_score,
        "Saturn_Drishti_Score": saturn_drishti_score,
        "Jupiter_Drishti_Score": jupiter_drishti_score,
        # Combustion Flags
        "Moon_Combust": moon_combust,
        "Mars_Combust": mars_combust,
        "Mercury_Combust": mercury_combust,
        "Jupiter_Combust": jupiter_combust,
        "Venus_Combust": venus_combust,
        "Saturn_Combust": saturn_combust,
        "Combust_Planets": combust_strings,
        "Combust_Count": combust_counts,
        # Angular Separations from Sun
        "Moon_Sun_Sep": moon_sep,
        "Mars_Sun_Sep": mars_sep,
        "Mercury_Sun_Sep": mercury_sep,
        "Jupiter_Sun_Sep": jupiter_sep,
        "Venus_Sun_Sep": venus_sep,
        "Saturn_Sun_Sep": saturn_sep,
    })
