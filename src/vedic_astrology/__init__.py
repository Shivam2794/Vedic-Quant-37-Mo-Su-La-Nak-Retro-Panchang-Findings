"""
Vedic Astrological Correlation Engine & Swiss Ephemeris Sidereal Module.

Exposes high-precision astronomical calculations, sidereal Lahiri ayanamsha,
9 Grahas kinematics, 27 Nakshatras & 108 Padas, Navamsha D9 divisional charts,
5 Panchang limbs, Parashari Drishti aspects, and Astangata combustion states.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from src.vedic_astrology.ephemeris import (
    DEFAULT_FLAGS,
    GRAHA_IDS,
    GRAHA_NAMES,
    calculate_9_grahas,
    calculate_graha_positions_batch,
    calculate_single_graha,
    datetime_to_julian_day,
    get_ayanamsha,
    init_ephemeris,
    timestamps_to_julian_day_array,
)
from src.vedic_astrology.nakshatra_navamsha import (
    NAKSHATRA_METADATA,
    NAKSHATRA_SPAN,
    PADA_SPAN,
    RASI_LORDS,
    RASI_NAMES,
    RASI_SPAN,
    get_nakshatra,
    get_nakshatra_batch,
    get_navamsha,
    get_navamsha_batch,
    is_gandanta,
    is_gandanta_batch,
)
from src.vedic_astrology.panchang import (
    FIXED_KARANAS,
    MOVEABLE_KARANAS,
    TITHI_BASE_NAMES,
    TITHI_NATURE_GROUPS,
    VARA_LORDS,
    VARA_NAMES,
    VARA_SANSKRIT,
    YOGA_NAMES,
    calculate_panchang,
    calculate_panchang_batch,
    get_karana_name,
    get_tithi_info,
)
from src.vedic_astrology.aspects_combustion import (
    COMBUSTION_ORBS_DIRECT,
    COMBUSTION_ORBS_RETROGRADE,
    PARASHARI_EXACT_ANGLES,
    PARASHARI_HOUSE_ASPECTS,
    angular_separation,
    angular_separation_batch,
    calculate_aspect_score,
    calculate_aspect_score_batch,
    calculate_aspects_and_combustion_batch,
    check_combustion,
    is_rasi_aspect,
    is_rasi_aspect_batch,
)


def calculate_all_vedic_features(
    jds_ut: Union[np.ndarray, pd.Series, List[float]],
    node_mode: str = "mean",
    orb_deg: float = 12.0,
) -> pd.DataFrame:
    """
    Unified high-performance pipeline that computes all Vedic astronomical and astrological
    features for an array or sequence of Julian Day numbers in Universal Time.

    Parameters
    ----------
    jds_ut : Union[np.ndarray, pd.Series, List[float]]
        Array of Julian Day numbers UT.
    node_mode : str
        'mean' or 'true' lunar node.
    orb_deg : float
        Orb in degrees for aspect strength scores.

    Returns
    -------
    pd.DataFrame
        Complete DataFrame containing 9 Grahas coordinates, Panchang limbs,
        Nakshatras, Navamsha D9 signs, Drishti aspects, and Combustion flags.
    """
    # 1. 9 Grahas Kinematics & Coordinates
    df_grahas = calculate_graha_positions_batch(jds_ut, node_mode=node_mode)

    # 2. 5 Panchang Limbs
    df_panchang = calculate_panchang_batch(
        sun_lons=df_grahas["Sun_Lon"],
        moon_lons=df_grahas["Moon_Lon"],
        jds_ut=df_grahas["Julian_Date_UT"],
    )

    # 3. Sun Nakshatra
    df_sun_nak = get_nakshatra_batch(df_grahas["Sun_Lon"])
    df_sun_nak = df_sun_nak.rename(columns={
        "Nakshatra_Num": "Sun_Nakshatra",
        "Nakshatra_Name": "Sun_Nakshatra_Name",
        "Pada": "Sun_Pada",
        "Global_Pada": "Sun_Global_Pada",
        "Nakshatra_Lord": "Sun_Nakshatra_Lord",
    })[["Sun_Nakshatra", "Sun_Nakshatra_Name", "Sun_Pada", "Sun_Nakshatra_Lord"]]

    # 4. Navamsha D9 Chart for Key Planets
    nav_bodies = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    nav_cols: Dict[str, Any] = {}
    for body in nav_bodies:
        df_nav = get_navamsha_batch(df_grahas[f"{body}_Lon"])
        nav_cols[f"{body}_Navamsha_Sign"] = df_nav["Navamsha_Sign_Name"]
        nav_cols[f"{body}_D1_Sign"] = df_nav["Rasi_Sign_Name"]
        if body in ("Sun", "Moon"):
            nav_cols[f"{body}_Vargottama"] = df_nav["Is_Vargottama"]

    df_nav_all = pd.DataFrame(nav_cols)

    # 5. Gandanta Junctions (Moon and Sun)
    moon_gandanta = is_gandanta_batch(df_grahas["Moon_Lon"])
    sun_gandanta = is_gandanta_batch(df_grahas["Sun_Lon"])
    df_gandanta = pd.DataFrame({
        "Moon_Gandanta": moon_gandanta,
        "Sun_Gandanta": sun_gandanta,
    })

    # 6. Parashari Drishti Aspects & Astangata Combustion
    df_aspects = calculate_aspects_and_combustion_batch(df_grahas, orb_deg=orb_deg)

    # Combine into a unified master DataFrame
    df_all = pd.concat([
        df_grahas,
        df_panchang,
        df_sun_nak,
        df_nav_all,
        df_gandanta,
        df_aspects,
    ], axis=1)

    return df_all


__all__ = [
    # Submodules
    "ephemeris",
    "nakshatra_navamsha",
    "panchang",
    "aspects_combustion",
    # Constants
    "DEFAULT_FLAGS",
    "GRAHA_IDS",
    "GRAHA_NAMES",
    "NAKSHATRA_METADATA",
    "NAKSHATRA_SPAN",
    "PADA_SPAN",
    "RASI_NAMES",
    "RASI_LORDS",
    "RASI_SPAN",
    "TITHI_BASE_NAMES",
    "TITHI_NATURE_GROUPS",
    "VARA_NAMES",
    "VARA_SANSKRIT",
    "VARA_LORDS",
    "YOGA_NAMES",
    "MOVEABLE_KARANAS",
    "FIXED_KARANAS",
    "PARASHARI_HOUSE_ASPECTS",
    "PARASHARI_EXACT_ANGLES",
    "COMBUSTION_ORBS_DIRECT",
    "COMBUSTION_ORBS_RETROGRADE",
    # Ephemeris functions
    "init_ephemeris",
    "datetime_to_julian_day",
    "timestamps_to_julian_day_array",
    "get_ayanamsha",
    "calculate_single_graha",
    "calculate_9_grahas",
    "calculate_graha_positions_batch",
    # Nakshatra & Navamsha functions
    "get_nakshatra",
    "get_nakshatra_batch",
    "get_navamsha",
    "get_navamsha_batch",
    "is_gandanta",
    "is_gandanta_batch",
    # Panchang functions
    "get_tithi_info",
    "get_karana_name",
    "calculate_panchang",
    "calculate_panchang_batch",
    # Aspects & Combustion functions
    "angular_separation",
    "angular_separation_batch",
    "is_rasi_aspect",
    "is_rasi_aspect_batch",
    "calculate_aspect_score",
    "calculate_aspect_score_batch",
    "check_combustion",
    "calculate_aspects_and_combustion_batch",
    # Master Unified Pipeline
    "calculate_all_vedic_features",
]
