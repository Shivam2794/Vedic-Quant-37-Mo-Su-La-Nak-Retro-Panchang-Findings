"""
Swiss Ephemeris Sidereal Lahiri 9 Grahas & Kinematics Engine.

Provides high-precision astronomical calculations for Vedic Quantitative Finance
using Swiss Ephemeris (`swisseph` / `pyswisseph`) configured with Lahiri Ayanamsha (Chitra Paksha).
Computes positions, speeds, distances, retrograde states, and ayanamsha values for:
Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu (North Node), and Ketu (South Node).
"""

from __future__ import annotations

import atexit
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import swisseph as swe

# Register cleanup on process termination
atexit.register(swe.close)

# Planetary Constants and Identifiers
GRAHA_IDS: Dict[str, int] = {
    "Sun": swe.SUN,          # 0
    "Moon": swe.MOON,        # 1
    "Mercury": swe.MERCURY,  # 2
    "Venus": swe.VENUS,      # 3
    "Mars": swe.MARS,        # 4
    "Jupiter": swe.JUPITER,  # 5
    "Saturn": swe.SATURN,    # 6
    "Rahu": swe.MEAN_NODE,   # 10 (Mean Node; 11 is True Node)
}

GRAHA_NAMES: List[str] = [
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"
]

# Standard Vedic Bitmask: Swiss Ephemeris algorithms + instantaneous speed + sidereal Lahiri frame
DEFAULT_FLAGS: int = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL

# Stationary threshold (degrees per day)
STATIONARY_SPEED_THRESHOLD: float = 0.05


def init_ephemeris(
    ephe_path: Optional[str] = None,
    sid_mode: int = swe.SIDM_LAHIRI,
    ayan_t0: float = 0.0,
    ayan_val: float = 0.0,
) -> None:
    """
    Initializes the Swiss Ephemeris subsystem with the specified sidereal ayanamsha mode.

    Parameters
    ----------
    ephe_path : Optional[str]
        Path to directory containing .se1 ephemeris files. If None, falls back to Moshier analytical model.
    sid_mode : int
        Swiss Ephemeris sidereal mode constant (default: swe.SIDM_LAHIRI).
    ayan_t0 : float
        Reference epoch t0 (default 0.0 for standard Lahiri).
    ayan_val : float
        Initial ayanamsha value at t0 (default 0.0 for standard Lahiri).
    """
    if ephe_path:
        swe.set_ephe_path(ephe_path)
    swe.set_sid_mode(sid_mode, ayan_t0, ayan_val)


# Initialize sidereal Lahiri mode on module load
init_ephemeris()


def datetime_to_julian_day(
    dt: Union[datetime, pd.Timestamp, str, np.datetime64],
    default_tz: str = "UTC",
) -> float:
    """
    Converts a timestamp to high-precision Julian Day Universal Time (JD UT).

    Parameters
    ----------
    dt : Union[datetime, pd.Timestamp, str, np.datetime64]
        Input timestamp. Can be timezone-aware or naive.
    default_tz : str
        Assumed timezone if dt is timezone-naive (default: 'UTC').

    Returns
    -------
    float
        Julian Day number in Universal Time (e.g. 2457388.500000).
    """
    if isinstance(dt, str):
        dt = pd.to_datetime(dt)
    elif isinstance(dt, np.datetime64):
        dt = pd.to_datetime(dt)

    if isinstance(dt, (datetime, pd.Timestamp)):
        if dt.tzinfo is None:
            # Localize naive timestamp to default_tz, then convert to UTC
            dt = pd.Timestamp(dt).tz_localize(default_tz).tz_convert("UTC")
        else:
            dt = pd.Timestamp(dt).tz_convert("UTC")
    else:
        dt = pd.Timestamp(dt).tz_convert("UTC")

    year = dt.year
    month = dt.month
    day = dt.day
    hour_float = dt.hour + dt.minute / 60.0 + (dt.second + dt.microsecond / 1e6) / 3600.0

    return float(swe.julday(year, month, day, hour_float, swe.GREG_CAL))


def timestamps_to_julian_day_array(
    timestamps: Union[pd.Series, pd.DatetimeIndex, np.ndarray, List[Any]],
    default_tz: str = "UTC",
) -> np.ndarray:
    """
    Vectorized conversion of a sequence of timestamps to an array of Julian Days UT.

    Parameters
    ----------
    timestamps : Union[pd.Series, pd.DatetimeIndex, np.ndarray, List[Any]]
        Sequence of timestamps.
    default_tz : str
        Assumed timezone if naive.

    Returns
    -------
    np.ndarray
        1D float64 array of Julian Days in Universal Time.
    """
    if isinstance(timestamps, (pd.DatetimeIndex, pd.Series)):
        ts_index = pd.DatetimeIndex(timestamps)
    else:
        ts_index = pd.to_datetime(timestamps)

    if ts_index.tz is None:
        ts_utc = ts_index.tz_localize(default_tz).tz_convert("UTC")
    else:
        ts_utc = ts_index.tz_convert("UTC")

    # High-precision microsecond-level JD computation from UTC epoch
    epoch = pd.Timestamp("1970-01-01", tz="UTC")
    seconds = (ts_utc - epoch).total_seconds()
    jds = 2440587.5 + (seconds / 86400.0)
    return np.asarray(jds, dtype=np.float64)


def get_ayanamsha(jd: float, sid_mode: int = swe.SIDM_LAHIRI) -> float:
    """
    Retrieves the exact Sidereal Ayanamsha (Chitra Paksha / Lahiri) in degrees for a given Julian Day UT.

    Parameters
    ----------
    jd : float
        Julian Day in Universal Time.
    sid_mode : int
        Sidereal mode (default: swe.SIDM_LAHIRI).

    Returns
    -------
    float
        Ayanamsha in degrees (e.g. ~24.19° in 2024).
    """
    swe.set_sid_mode(sid_mode, 0.0, 0.0)
    return float(swe.get_ayanamsa_ut(jd))


def calculate_single_graha(
    jd: float,
    planet_id: int,
    flags: int = DEFAULT_FLAGS,
) -> Tuple[float, float, float, float, float, float]:
    """
    Calculates 3D sidereal coordinates and instantaneous kinematic speeds for a single celestial body.

    Parameters
    ----------
    jd : float
        Julian Day UT.
    planet_id : int
        Swiss Ephemeris body identifier (e.g. swe.SUN, swe.MOON).
    flags : int
        Computation flags bitmask.

    Returns
    -------
    Tuple[float, float, float, float, float, float]
        (longitude_deg, latitude_deg, distance_au, speed_lon_deg_day, speed_lat_deg_day, speed_dist_au_day)
    """
    res, ret_flag = swe.calc_ut(jd, planet_id, flags)
    lon, lat, dist, speed_lon, speed_lat, speed_dist = res
    # Ensure longitude is normalized in [0, 360)
    lon = lon % 360.0
    return (float(lon), float(lat), float(dist), float(speed_lon), float(speed_lat), float(speed_dist))


def calculate_9_grahas(
    jd: float,
    node_mode: str = "mean",
    flags: int = DEFAULT_FLAGS,
) -> Dict[str, Dict[str, Union[float, bool]]]:
    """
    Calculates Sidereal Lahiri coordinates, speeds, distances, and retrograde flags for all 9 Vedic Grahas.

    Parameters
    ----------
    jd : float
        Julian Day in Universal Time.
    node_mode : str
        'mean' for Mean Lunar Node (swe.MEAN_NODE, classical standard) or 'true' for True Lunar Node (swe.TRUE_NODE).
    flags : int
        Computation flags bitmask.

    Returns
    -------
    Dict[str, Dict[str, Union[float, bool]]]
        Dictionary keyed by Graha name containing coordinates, speed, and retrograde booleans.
    """
    results: Dict[str, Dict[str, Union[float, bool]]] = {}

    # 1. Physical Grahas: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn
    physical_grahas = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
    }

    for name, pid in physical_grahas.items():
        lon, lat, dist, speed_lon, speed_lat, speed_dist = calculate_single_graha(jd, pid, flags)
        is_retro = bool(speed_lon < 0.0)
        is_stat = bool(abs(speed_lon) < STATIONARY_SPEED_THRESHOLD)
        results[name] = {
            "lon": lon,
            "lat": lat,
            "dist": dist,
            "speed": speed_lon,
            "speed_lat": speed_lat,
            "speed_dist": speed_dist,
            "is_retrograde": is_retro,
            "is_stationary": is_stat,
        }

    # 2. Rahu (North Node)
    node_pid = swe.TRUE_NODE if node_mode.lower() == "true" else swe.MEAN_NODE
    r_lon, r_lat, r_dist, r_speed_lon, r_speed_lat, r_speed_dist = calculate_single_graha(jd, node_pid, flags)
    r_is_retro = bool(r_speed_lon < 0.0)
    r_is_stat = bool(abs(r_speed_lon) < STATIONARY_SPEED_THRESHOLD)
    results["Rahu"] = {
        "lon": r_lon,
        "lat": r_lat,
        "dist": r_dist,
        "speed": r_speed_lon,
        "speed_lat": r_speed_lat,
        "speed_dist": r_speed_dist,
        "is_retrograde": r_is_retro,
        "is_stationary": r_is_stat,
    }

    # 3. Ketu (South Node) — Exactly 180° opposite to Rahu
    k_lon = (r_lon + 180.0) % 360.0
    k_lat = -r_lat
    k_dist = r_dist
    k_speed_lon = r_speed_lon
    k_speed_lat = -r_speed_lat
    k_speed_dist = r_speed_dist
    k_is_retro = bool(k_speed_lon < 0.0) if node_mode.lower() == "true" else True
    k_is_stat = bool(abs(k_speed_lon) < STATIONARY_SPEED_THRESHOLD)
    results["Ketu"] = {
        "lon": k_lon,
        "lat": k_lat,
        "dist": k_dist,
        "speed": k_speed_lon,
        "speed_lat": k_speed_lat,
        "speed_dist": k_speed_dist,
        "is_retrograde": k_is_retro,
        "is_stationary": k_is_stat,
    }

    return results


def calculate_graha_positions_batch(
    jds: Union[np.ndarray, pd.Series, List[float]],
    node_mode: str = "mean",
    flags: int = DEFAULT_FLAGS,
) -> pd.DataFrame:
    """
    Vectorized high-performance batch computation of 9 Graha coordinates for an array of Julian Days UT.

    Parameters
    ----------
    jds : Union[np.ndarray, pd.Series, List[float]]
        Sequence or array of Julian Day UT numbers.
    node_mode : str
        'mean' or 'true'.
    flags : int
        Computation flags bitmask.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns for Julian_Date_UT, 9 Graha coordinates, speeds, retrograde booleans, and Ayanamsha.
    """
    jds_arr = np.asarray(jds, dtype=np.float64)
    n_pts = len(jds_arr)

    # Pre-allocate output arrays
    cols_dict: Dict[str, np.ndarray] = {
        "Julian_Date_UT": jds_arr,
    }

    for g in GRAHA_NAMES:
        cols_dict[f"{g}_Lon"] = np.empty(n_pts, dtype=np.float64)
        cols_dict[f"{g}_Lat"] = np.empty(n_pts, dtype=np.float64)
        cols_dict[f"{g}_Dist"] = np.empty(n_pts, dtype=np.float64)
        cols_dict[f"{g}_Speed"] = np.empty(n_pts, dtype=np.float64)
        cols_dict[f"{g}_Retrograde"] = np.empty(n_pts, dtype=bool)

    ayan_arr = np.empty(n_pts, dtype=np.float64)

    node_pid = swe.TRUE_NODE if node_mode.lower() == "true" else swe.MEAN_NODE
    bodies = [
        ("Sun", swe.SUN),
        ("Moon", swe.MOON),
        ("Mars", swe.MARS),
        ("Mercury", swe.MERCURY),
        ("Jupiter", swe.JUPITER),
        ("Venus", swe.VENUS),
        ("Saturn", swe.SATURN),
        ("Rahu", node_pid),
    ]

    for i in range(n_pts):
        jd_val = jds_arr[i]
        ayan_arr[i] = swe.get_ayanamsa_ut(jd_val)

        for name, pid in bodies:
            res, _ = swe.calc_ut(jd_val, pid, flags)
            lon = res[0] % 360.0
            lat = res[1]
            dist = res[2]
            spd = res[3]
            cols_dict[f"{name}_Lon"][i] = lon
            cols_dict[f"{name}_Lat"][i] = lat
            cols_dict[f"{name}_Dist"][i] = dist
            cols_dict[f"{name}_Speed"][i] = spd
            cols_dict[f"{name}_Retrograde"][i] = spd < 0.0

        # Ketu derived from Rahu
        r_lon = cols_dict["Rahu_Lon"][i]
        r_lat = cols_dict["Rahu_Lat"][i]
        r_dist = cols_dict["Rahu_Dist"][i]
        r_spd = cols_dict["Rahu_Speed"][i]

        k_lon = (r_lon + 180.0) % 360.0
        k_lat = -r_lat
        k_dist = r_dist
        k_spd = r_spd

        cols_dict["Ketu_Lon"][i] = k_lon
        cols_dict["Ketu_Lat"][i] = k_lat
        cols_dict["Ketu_Dist"][i] = k_dist
        cols_dict["Ketu_Speed"][i] = k_spd
        cols_dict["Ketu_Retrograde"][i] = k_spd < 0.0 if node_mode.lower() == "true" else True

    cols_dict["Ayanamsha_Val"] = ayan_arr
    return pd.DataFrame(cols_dict)
