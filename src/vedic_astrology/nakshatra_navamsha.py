"""
Nakshatra, Pada, and Navamsha (D9) Divisional Chart Engine.

Provides exact astronomical and mathematical mapping for:
- 27 Sidereal Nakshatras (13°20' / 800' each) with Sanskrit names, Vimshottari lords, deities, ganas, and symbols.
- 108 Padas (3°20' / 200' each).
- Navamsha (D9) Chart: Sign index = floor(lon / 3.33333333°) % 12, sign names, ruling lords, and Vargottama detection.
- Gandanta junction detection (Sandhi across water-fire sign boundaries).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

# 27 Nakshatras Complete Metadata Table
NAKSHATRA_METADATA: List[Dict[str, Any]] = [
    {
        "index": 1,
        "name": "Ashwini",
        "sanskrit": "अश्विनी",
        "lord": "Ketu",
        "deity": "Ashwini Kumaras",
        "gana": "Deva",
        "symbol": "Horse's Head",
        "start_deg": 0.0,
        "end_deg": 13.333333333333334,
        "element": "Fire",
    },
    {
        "index": 2,
        "name": "Bharani",
        "sanskrit": "भरणी",
        "lord": "Venus",
        "deity": "Yama",
        "gana": "Manushya",
        "symbol": "Yoni",
        "start_deg": 13.333333333333334,
        "end_deg": 26.666666666666668,
        "element": "Fire",
    },
    {
        "index": 3,
        "name": "Krittika",
        "sanskrit": "कृत्तिका",
        "lord": "Sun",
        "deity": "Agni",
        "gana": "Rakshasa",
        "symbol": "Knife / Flame",
        "start_deg": 26.666666666666668,
        "end_deg": 40.0,
        "element": "Fire/Earth",
    },
    {
        "index": 4,
        "name": "Rohini",
        "sanskrit": "रोहिणी",
        "lord": "Moon",
        "deity": "Brahma / Prajapati",
        "gana": "Manushya",
        "symbol": "Cart / Chariot",
        "start_deg": 40.0,
        "end_deg": 53.333333333333336,
        "element": "Earth",
    },
    {
        "index": 5,
        "name": "Mrigashira",
        "sanskrit": "मृगशिरा",
        "lord": "Mars",
        "deity": "Soma / Chandra",
        "gana": "Deva",
        "symbol": "Deer's Head",
        "start_deg": 53.333333333333336,
        "end_deg": 66.66666666666667,
        "element": "Earth/Air",
    },
    {
        "index": 6,
        "name": "Ardra",
        "sanskrit": "आर्द्रा",
        "lord": "Rahu",
        "deity": "Rudra",
        "gana": "Manushya",
        "symbol": "Teardrop / Diamond",
        "start_deg": 66.66666666666667,
        "end_deg": 80.0,
        "element": "Air",
    },
    {
        "index": 7,
        "name": "Punarvasu",
        "sanskrit": "पुनर्वसु",
        "lord": "Jupiter",
        "deity": "Aditi",
        "gana": "Deva",
        "symbol": "Bow and Quiver",
        "start_deg": 80.0,
        "end_deg": 93.33333333333333,
        "element": "Air/Water",
    },
    {
        "index": 8,
        "name": "Pushya",
        "sanskrit": "पुष्य",
        "lord": "Saturn",
        "deity": "Brihaspati",
        "gana": "Deva",
        "symbol": "Cow's Udder / Lotus",
        "start_deg": 93.33333333333333,
        "end_deg": 106.66666666666667,
        "element": "Water",
    },
    {
        "index": 9,
        "name": "Ashlesha",
        "sanskrit": "आश्लेषा",
        "lord": "Mercury",
        "deity": "Sarpas / Nagas",
        "gana": "Rakshasa",
        "symbol": "Coiled Serpent",
        "start_deg": 106.66666666666667,
        "end_deg": 120.0,
        "element": "Water",
    },
    {
        "index": 10,
        "name": "Magha",
        "sanskrit": "मघा",
        "lord": "Ketu",
        "deity": "Pitris",
        "gana": "Rakshasa",
        "symbol": "Royal Throne",
        "start_deg": 120.0,
        "end_deg": 133.33333333333334,
        "element": "Fire",
    },
    {
        "index": 11,
        "name": "Purva Phalguni",
        "sanskrit": "पूर्वाफाल्गुनी",
        "lord": "Venus",
        "deity": "Bhaga",
        "gana": "Manushya",
        "symbol": "Front Legs of Bed",
        "start_deg": 133.33333333333334,
        "end_deg": 146.66666666666666,
        "element": "Fire",
    },
    {
        "index": 12,
        "name": "Uttara Phalguni",
        "sanskrit": "उत्तराफाल्गुनी",
        "lord": "Sun",
        "deity": "Aryaman",
        "gana": "Manushya",
        "symbol": "Back Legs of Bed",
        "start_deg": 146.66666666666666,
        "end_deg": 160.0,
        "element": "Fire/Earth",
    },
    {
        "index": 13,
        "name": "Hasta",
        "sanskrit": "हस्त",
        "lord": "Moon",
        "deity": "Savitur",
        "gana": "Deva",
        "symbol": "Hand / Closed Fist",
        "start_deg": 160.0,
        "end_deg": 173.33333333333334,
        "element": "Earth",
    },
    {
        "index": 14,
        "name": "Chitra",
        "sanskrit": "चित्रा",
        "lord": "Mars",
        "deity": "Vishvakarma / Tvashtar",
        "gana": "Rakshasa",
        "symbol": "Pearl / Jewel",
        "start_deg": 173.33333333333334,
        "end_deg": 186.66666666666666,
        "element": "Earth/Air",
    },
    {
        "index": 15,
        "name": "Swati",
        "sanskrit": "स्वाती",
        "lord": "Rahu",
        "deity": "Vayu",
        "gana": "Deva",
        "symbol": "Young Shoot / Sword",
        "start_deg": 186.66666666666666,
        "end_deg": 200.0,
        "element": "Air",
    },
    {
        "index": 16,
        "name": "Vishakha",
        "sanskrit": "विशाखा",
        "lord": "Jupiter",
        "deity": "Indragni",
        "gana": "Rakshasa",
        "symbol": "Triumphal Arch",
        "start_deg": 200.0,
        "end_deg": 213.33333333333334,
        "element": "Air/Water",
    },
    {
        "index": 17,
        "name": "Anuradha",
        "sanskrit": "अनुराधा",
        "lord": "Saturn",
        "deity": "Mitra",
        "gana": "Deva",
        "symbol": "Lotus / Archway",
        "start_deg": 213.33333333333334,
        "end_deg": 226.66666666666666,
        "element": "Water",
    },
    {
        "index": 18,
        "name": "Jyeshtha",
        "sanskrit": "ज्येष्ठा",
        "lord": "Mercury",
        "deity": "Indra",
        "gana": "Rakshasa",
        "symbol": "Circular Amulet / Umbrella",
        "start_deg": 226.66666666666666,
        "end_deg": 240.0,
        "element": "Water",
    },
    {
        "index": 19,
        "name": "Mula",
        "sanskrit": "मूल",
        "lord": "Ketu",
        "deity": "Nirriti",
        "gana": "Rakshasa",
        "symbol": "Bunch of Roots",
        "start_deg": 240.0,
        "end_deg": 253.33333333333334,
        "element": "Fire",
    },
    {
        "index": 20,
        "name": "Purva Ashadha",
        "sanskrit": "पूर्वाषाढ़ा",
        "lord": "Venus",
        "deity": "Apas",
        "gana": "Manushya",
        "symbol": "Elephant Tusk / Fan",
        "start_deg": 253.33333333333334,
        "end_deg": 266.6666666666667,
        "element": "Fire",
    },
    {
        "index": 21,
        "name": "Uttara Ashadha",
        "sanskrit": "उत्तराषाढ़ा",
        "lord": "Sun",
        "deity": "Vishvedevas",
        "gana": "Manushya",
        "symbol": "Small Bed / Planks",
        "start_deg": 266.6666666666667,
        "end_deg": 280.0,
        "element": "Fire/Earth",
    },
    {
        "index": 22,
        "name": "Shravana",
        "sanskrit": "श्रवण",
        "lord": "Moon",
        "deity": "Vishnu",
        "gana": "Deva",
        "symbol": "Ear / Three Footprints",
        "start_deg": 280.0,
        "end_deg": 293.3333333333333,
        "element": "Earth",
    },
    {
        "index": 23,
        "name": "Dhanishta",
        "sanskrit": "धनिष्ठा",
        "lord": "Mars",
        "deity": "Eight Vasus",
        "gana": "Rakshasa",
        "symbol": "Drum (Mridangam) / Flute",
        "start_deg": 293.3333333333333,
        "end_deg": 306.6666666666667,
        "element": "Earth/Air",
    },
    {
        "index": 24,
        "name": "Shatabhisha",
        "sanskrit": "शतभिषा",
        "lord": "Rahu",
        "deity": "Varuna",
        "gana": "Rakshasa",
        "symbol": "100 Physicians / Empty Circle",
        "start_deg": 306.6666666666667,
        "end_deg": 320.0,
        "element": "Air",
    },
    {
        "index": 25,
        "name": "Purva Bhadrapada",
        "sanskrit": "पूर्वभाद्रपदा",
        "lord": "Jupiter",
        "deity": "Aja Ekapada",
        "gana": "Manushya",
        "symbol": "Two Front Legs of Bed / Sword",
        "start_deg": 320.0,
        "end_deg": 333.33333333333334,
        "element": "Air/Water",
    },
    {
        "index": 26,
        "name": "Uttara Bhadrapada",
        "sanskrit": "उत्तरभाद्रपदा",
        "lord": "Saturn",
        "deity": "Ahirbudhnya",
        "gana": "Manushya",
        "symbol": "Two Back Legs of Bed / Serpent",
        "start_deg": 333.33333333333334,
        "end_deg": 346.6666666666667,
        "element": "Water",
    },
    {
        "index": 27,
        "name": "Revati",
        "sanskrit": "रेवती",
        "lord": "Mercury",
        "deity": "Pushan",
        "gana": "Deva",
        "symbol": "Fish / Pair of Fish",
        "start_deg": 346.6666666666667,
        "end_deg": 360.0,
        "element": "Water",
    },
]

# Zodiac Rasi (Sign) Names & Ruling Planetary Lords (0=Aries, ..., 11=Pisces)
RASI_NAMES: List[str] = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

RASI_LORDS: List[str] = [
    "Mars", "Venus", "Mercury", "Moon",
    "Sun", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Saturn", "Jupiter"
]

# Constants
NAKSHATRA_SPAN: float = 360.0 / 27.0  # 13.333333333333334° (13°20')
PADA_SPAN: float = 360.0 / 108.0      # 3.3333333333333335° (3°20')
RASI_SPAN: float = 30.0               # 30°


def get_nakshatra(lon_deg: float) -> Dict[str, Any]:
    """
    Computes the Nakshatra, Pada, and associated Vedic attributes for a given sidereal longitude.

    Parameters
    ----------
    lon_deg : float
        Sidereal longitude in degrees [0, 360).

    Returns
    -------
    Dict[str, Any]
        Dictionary containing Nakshatra number (1-27), name, Pada (1-4), Lord, Deity, Gana, and Global Pada (0-107).
    """
    lon = float(lon_deg) % 360.0
    global_pada = int(np.floor(((lon % 360.0) + 1e-9) / PADA_SPAN)) % 108
    nak_idx = global_pada // 4
    pada = (global_pada % 4) + 1

    nak_info = NAKSHATRA_METADATA[nak_idx]

    return {
        "nakshatra_num": nak_info["index"],
        "nakshatra_name": nak_info["name"],
        "sanskrit": nak_info["sanskrit"],
        "pada": pada,
        "global_pada": global_pada,
        "lord": nak_info["lord"],
        "deity": nak_info["deity"],
        "gana": nak_info["gana"],
        "symbol": nak_info["symbol"],
    }


def get_nakshatra_batch(lons: Union[np.ndarray, pd.Series, List[float]]) -> pd.DataFrame:
    """
    Vectorized computation of Nakshatra, Pada, and attributes for an array of sidereal longitudes.

    Parameters
    ----------
    lons : Union[np.ndarray, pd.Series, List[float]]
        Sequence or array of sidereal longitudes [0, 360).

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: Nakshatra_Num, Nakshatra_Name, Pada, Global_Pada, Nakshatra_Lord, Deity, Gana.
    """
    lons_arr = np.asarray(lons, dtype=np.float64) % 360.0
    global_padas = (np.floor((lons_arr + 1e-9) / PADA_SPAN).astype(int)) % 108
    nak_indices = global_padas // 4
    padas = (global_padas % 4) + 1

    names = [NAKSHATRA_METADATA[idx]["name"] for idx in nak_indices]
    lords = [NAKSHATRA_METADATA[idx]["lord"] for idx in nak_indices]
    deities = [NAKSHATRA_METADATA[idx]["deity"] for idx in nak_indices]
    ganas = [NAKSHATRA_METADATA[idx]["gana"] for idx in nak_indices]

    return pd.DataFrame({
        "Nakshatra_Num": nak_indices + 1,
        "Nakshatra_Name": names,
        "Pada": padas,
        "Global_Pada": global_padas,
        "Nakshatra_Lord": lords,
        "Deity": deities,
        "Gana": ganas,
    })


def get_navamsha(lon_deg: float) -> Dict[str, Any]:
    """
    Calculates the Navamsha (D9) harmonic divisional chart sign, lord, and Vargottama state.

    Mathematical Identity:
    Navamsha Sign Index (0-11) = floor(lon / 3.33333333°) % 12
    Rasi (D1) Sign Index (0-11) = floor(lon / 30.0°) % 12
    Vargottama = (D1 == D9)

    Parameters
    ----------
    lon_deg : float
        Sidereal longitude in degrees [0, 360).

    Returns
    -------
    Dict[str, Any]
        Dictionary with Navamsha sign index (0-11), sign name, ruling lord, D1 Rasi sign, and Vargottama boolean.
    """
    lon = float(lon_deg) % 360.0
    global_pada = int(np.floor(((lon % 360.0) + 1e-9) / PADA_SPAN)) % 108
    nav_idx = global_pada % 12
    rasi_idx = int(np.floor(((lon % 360.0) + 1e-9) / RASI_SPAN)) % 12

    return {
        "navamsha_sign_num": nav_idx,
        "navamsha_sign_name": RASI_NAMES[nav_idx],
        "navamsha_lord": RASI_LORDS[nav_idx],
        "rasi_sign_num": rasi_idx,
        "rasi_sign_name": RASI_NAMES[rasi_idx],
        "is_vargottama": bool(nav_idx == rasi_idx),
    }


def get_navamsha_batch(lons: Union[np.ndarray, pd.Series, List[float]]) -> pd.DataFrame:
    """
    Vectorized computation of Navamsha (D9) chart attributes for an array of sidereal longitudes.

    Parameters
    ----------
    lons : Union[np.ndarray, pd.Series, List[float]]
        Sequence or array of sidereal longitudes [0, 360).

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: Navamsha_Sign_Num, Navamsha_Sign_Name, Navamsha_Lord, Rasi_Sign_Num, Rasi_Sign_Name, Is_Vargottama.
    """
    lons_arr = np.asarray(lons, dtype=np.float64) % 360.0
    global_padas = (np.floor((lons_arr + 1e-9) / PADA_SPAN).astype(int)) % 108
    nav_indices = global_padas % 12
    rasi_indices = (np.floor((lons_arr + 1e-9) / RASI_SPAN).astype(int)) % 12

    nav_names = [RASI_NAMES[i] for i in nav_indices]
    nav_lords = [RASI_LORDS[i] for i in nav_indices]
    rasi_names = [RASI_NAMES[i] for i in rasi_indices]
    is_vargottama = (nav_indices == rasi_indices)

    return pd.DataFrame({
        "Navamsha_Sign_Num": nav_indices,
        "Navamsha_Sign_Name": nav_names,
        "Navamsha_Lord": nav_lords,
        "Rasi_Sign_Num": rasi_indices,
        "Rasi_Sign_Name": rasi_names,
        "Is_Vargottama": is_vargottama,
    })


def is_gandanta(lon_deg: float, threshold_deg: float = 0.8) -> bool:
    """
    Determines if a celestial longitude falls within a Gandanta junction (Sandhi).
    Gandanta points occur at the 3 Water -> Fire sign junctures:
    1. Pisces (360° / 0°) -> Aries (0°)
    2. Cancer (120°) -> Leo (120°)
    3. Scorpio (240°) -> Sagittarius (240°)

    Parameters
    ----------
    lon_deg : float
        Sidereal longitude in degrees [0, 360).
    threshold_deg : float
        Angular window around the juncture (default 0.8° = 48 arcminutes).

    Returns
    -------
    bool
        True if the position is within the Gandanta orb.
    """
    lon = float(lon_deg) % 360.0
    # Junction 1: 0° / 360°
    if lon <= threshold_deg or lon >= (360.0 - threshold_deg):
        return True
    # Junction 2: 120°
    if abs(lon - 120.0) <= threshold_deg:
        return True
    # Junction 3: 240°
    if abs(lon - 240.0) <= threshold_deg:
        return True
    return False


def is_gandanta_batch(
    lons: Union[np.ndarray, pd.Series, List[float]],
    threshold_deg: float = 0.8,
) -> np.ndarray:
    """
    Vectorized Gandanta detection for an array of celestial longitudes.

    Parameters
    ----------
    lons : Union[np.ndarray, pd.Series, List[float]]
        Sequence or array of sidereal longitudes.
    threshold_deg : float
        Angular window around junctures.

    Returns
    -------
    np.ndarray
        Boolean array indicating Gandanta status.
    """
    lons_arr = np.asarray(lons, dtype=np.float64) % 360.0
    c1 = (lons_arr <= threshold_deg) | (lons_arr >= (360.0 - threshold_deg))
    c2 = np.abs(lons_arr - 120.0) <= threshold_deg
    c3 = np.abs(lons_arr - 240.0) <= threshold_deg
    return c1 | c2 | c3
