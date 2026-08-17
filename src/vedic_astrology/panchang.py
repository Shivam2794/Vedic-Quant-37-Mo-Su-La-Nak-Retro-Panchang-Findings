"""
Vedic Panchang (5 Limbs of Time) Engine.

Calculates the 5 classical Panchang limbs from Sun and Moon sidereal coordinates and Julian Date:
1. Tithi (1-30, Shukla 1-15, Krishna 16-30, Paksha, and nature)
2. Vara (0-6, Sunday to Saturday with ruling Graha lords)
3. Nakshatra (1-27 Moon's sidereal mansion and Pada)
4. Nithya Yoga (1-27 Luni-Solar combined angular motion with Vyatipata & Vaidhriti detection)
5. Karana (1-60 Half-Tithi with 4 Fixed + 7 Repeating Moveable Karanas and Vishti/Bhadra detection)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from src.vedic_astrology.nakshatra_navamsha import (
    NAKSHATRA_METADATA,
    NAKSHATRA_SPAN,
    PADA_SPAN,
    get_nakshatra,
)

# 1. Tithi Names (1-15 Shukla, 16-30 Krishna)
TITHI_BASE_NAMES: List[str] = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashti", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima"
]

TITHI_NATURE_GROUPS: List[str] = [
    "Nanda", "Bhadra", "Jaya", "Rikta", "Poorna"
]

# 2. Vara (Weekday) Names and Lords
VARA_NAMES: List[str] = [
    "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
]
VARA_SANSKRIT: List[str] = [
    "Ravivara", "Somavara", "Mangalavara", "Budhavara", "Guruvara", "Shukravara", "Shanivara"
]
VARA_LORDS: List[str] = [
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"
]

# 4. 27 Nithya Yoga Names
YOGA_NAMES: List[str] = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti"
]

# 5. Karana Names
MOVEABLE_KARANAS: List[str] = [
    "Bava", "Balava", "Kaulava", "Taitila", "Garija", "Vanija", "Vishti"
]

FIXED_KARANAS: Dict[int, str] = {
    1: "Kintughna",
    58: "Shakuni",
    59: "Chatushpada",
    60: "Naga",
}


def get_tithi_info(tithi_num: int) -> Dict[str, str]:
    """
    Returns descriptive metadata for a given Tithi number (1-30).
    """
    t = min(max(int(tithi_num), 1), 30)
    if t <= 15:
        paksha = "Shukla"
        base_name = TITHI_BASE_NAMES[t - 1]
    else:
        paksha = "Krishna"
        base_idx = t - 16
        base_name = "Amavasya" if t == 30 else TITHI_BASE_NAMES[base_idx]

    full_name = f"{paksha} {base_name}"
    nature = TITHI_NATURE_GROUPS[(t - 1) % 5]

    return {
        "tithi_num": t,
        "tithi_name": full_name,
        "paksha": paksha,
        "tithi_base_name": base_name,
        "tithi_nature": nature,
    }


def get_karana_name(karana_num: int) -> str:
    """
    Returns the Karana name for a given Karana index (1-60).
    """
    k = min(max(int(karana_num), 1), 60)
    if k in FIXED_KARANAS:
        return FIXED_KARANAS[k]
    return MOVEABLE_KARANAS[(k - 2) % 7]


def calculate_panchang(
    sun_lon_deg: float,
    moon_lon_deg: float,
    jd_ut: float,
) -> Dict[str, Any]:
    """
    Calculates the 5 Panchang Limbs for a single point in time.

    Parameters
    ----------
    sun_lon_deg : float
        Sun sidereal longitude in degrees [0, 360).
    moon_lon_deg : float
        Moon sidereal longitude in degrees [0, 360).
    jd_ut : float
        Julian Day in Universal Time.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing all 5 limbs and derived Vedic flags.
    """
    sun_lon = float(sun_lon_deg) % 360.0
    moon_lon = float(moon_lon_deg) % 360.0
    jd = float(jd_ut)

    # 1. Tithi: floor(((Moon - Sun) % 360) / 12) + 1
    elongation = (moon_lon - sun_lon) % 360.0
    tithi_num = int(np.floor(elongation / 12.0)) + 1
    tithi_num = min(max(tithi_num, 1), 30)
    tithi_info = get_tithi_info(tithi_num)

    # 2. Vara: floor(JD + 1.5) % 7 (0=Sunday, ..., 6=Saturday)
    vara_num = int(np.floor(jd + 1.5)) % 7
    vara_name = VARA_NAMES[vara_num]
    vara_sanskrit = VARA_SANSKRIT[vara_num]
    vara_lord = VARA_LORDS[vara_num]

    # 3. Nakshatra: Moon's sidereal Nakshatra (1-27)
    nak_info = get_nakshatra(moon_lon)

    # 4. Nithya Yoga: floor(((Sun + Moon) % 360) / (360 / 27)) + 1
    sol_lun_sum = (sun_lon + moon_lon) % 360.0
    yoga_num = int(np.floor(sol_lun_sum / NAKSHATRA_SPAN)) + 1
    yoga_num = min(max(yoga_num, 1), 27)
    yoga_name = YOGA_NAMES[yoga_num - 1]
    is_vyatipata = bool(yoga_num == 17)
    is_vaidhriti = bool(yoga_num == 27)

    # 5. Karana: floor(elongation / 6) + 1
    karana_num = int(np.floor(elongation / 6.0)) + 1
    karana_num = min(max(karana_num, 1), 60)
    karana_name = get_karana_name(karana_num)
    is_vishti = bool(karana_name == "Vishti")

    return {
        # Tithi Limb
        "tithi_num": tithi_num,
        "tithi_name": tithi_info["tithi_name"],
        "paksha": tithi_info["paksha"],
        "tithi_nature": tithi_info["tithi_nature"],
        "moon_sun_elongation": elongation,
        # Vara Limb
        "vara_num": vara_num,
        "vara_name": vara_name,
        "vara_sanskrit": vara_sanskrit,
        "vara_lord": vara_lord,
        # Nakshatra Limb
        "moon_nakshatra_num": nak_info["nakshatra_num"],
        "moon_nakshatra_name": nak_info["nakshatra_name"],
        "moon_pada": nak_info["pada"],
        "moon_nakshatra_lord": nak_info["lord"],
        # Yoga Limb
        "yoga_num": yoga_num,
        "yoga_name": yoga_name,
        "is_vyatipata_yoga": is_vyatipata,
        "is_vaidhriti_yoga": is_vaidhriti,
        # Karana Limb
        "karana_num": karana_num,
        "karana_name": karana_name,
        "is_vishti_karana": is_vishti,
    }


def calculate_panchang_batch(
    sun_lons: Union[np.ndarray, pd.Series, List[float]],
    moon_lons: Union[np.ndarray, pd.Series, List[float]],
    jds_ut: Union[np.ndarray, pd.Series, List[float]],
) -> pd.DataFrame:
    """
    Vectorized batch computation of 5 Panchang Limbs for arrays of astronomical coordinates.

    Parameters
    ----------
    sun_lons : Union[np.ndarray, pd.Series, List[float]]
        Array of Sun sidereal longitudes [0, 360).
    moon_lons : Union[np.ndarray, pd.Series, List[float]]
        Array of Moon sidereal longitudes [0, 360).
    jds_ut : Union[np.ndarray, pd.Series, List[float]]
        Array of Julian Day numbers in Universal Time.

    Returns
    -------
    pd.DataFrame
        DataFrame with full Panchang columns matching project schema.
    """
    s_lons = np.asarray(sun_lons, dtype=np.float64) % 360.0
    m_lons = np.asarray(moon_lons, dtype=np.float64) % 360.0
    jds = np.asarray(jds_ut, dtype=np.float64)
    n = len(s_lons)

    # 1. Tithi
    elongation = (m_lons - s_lons) % 360.0
    tithi_nums = np.floor(elongation / 12.0).astype(int) + 1
    tithi_nums = np.clip(tithi_nums, 1, 30)

    pakshas = np.where(tithi_nums <= 15, "Shukla", "Krishna")
    tithi_names = []
    for t in tithi_nums:
        info = get_tithi_info(t)
        tithi_names.append(info["tithi_name"])

    # 2. Vara
    vara_nums = (np.floor(jds + 1.5).astype(int)) % 7
    vara_names = [VARA_NAMES[v] for v in vara_nums]
    vara_lords = [VARA_LORDS[v] for v in vara_nums]

    # 3. Nakshatra (Moon)
    nak_indices = np.floor(m_lons / NAKSHATRA_SPAN).astype(int)
    nak_indices = np.clip(nak_indices, 0, 26)
    nak_padas = (np.floor((m_lons % NAKSHATRA_SPAN) / PADA_SPAN).astype(int) + 1)
    nak_padas = np.clip(nak_padas, 1, 4)

    moon_nak_names = [NAKSHATRA_METADATA[idx]["name"] for idx in nak_indices]
    moon_nak_lords = [NAKSHATRA_METADATA[idx]["lord"] for idx in nak_indices]

    # 4. Nithya Yoga
    sol_lun_sums = (s_lons + m_lons) % 360.0
    yoga_nums = np.floor(sol_lun_sums / NAKSHATRA_SPAN).astype(int) + 1
    yoga_nums = np.clip(yoga_nums, 1, 27)
    yoga_names = [YOGA_NAMES[y - 1] for y in yoga_nums]
    is_vyatipata = (yoga_nums == 17)
    is_vaidhriti = (yoga_nums == 27)

    # 5. Karana
    karana_nums = np.floor(elongation / 6.0).astype(int) + 1
    karana_nums = np.clip(karana_nums, 1, 60)
    karana_names = [get_karana_name(k) for k in karana_nums]
    is_vishti = np.array([name == "Vishti" for name in karana_names], dtype=bool)

    return pd.DataFrame({
        # Tithi
        "Tithi_Num": tithi_nums,
        "Tithi_Name": tithi_names,
        "Paksha": pakshas,
        "Moon_Sun_Elongation": elongation,
        # Vara
        "Vara_Num": vara_nums,
        "Vara_Name": vara_names,
        "Vara_Lord": vara_lords,
        # Nakshatra
        "Moon_Nakshatra": nak_indices + 1,
        "Moon_Nakshatra_Name": moon_nak_names,
        "Moon_Pada": nak_padas,
        "Moon_Nakshatra_Lord": moon_nak_lords,
        # Yoga
        "Yoga_Num": yoga_nums,
        "Yoga_Name": yoga_names,
        "Is_Vyatipata_Yoga": is_vyatipata,
        "Is_Vaidhriti_Yoga": is_vaidhriti,
        # Karana
        "Karana_Num": karana_nums,
        "Karana_Name": karana_names,
        "Is_Vishti_Karana": is_vishti,
    })
