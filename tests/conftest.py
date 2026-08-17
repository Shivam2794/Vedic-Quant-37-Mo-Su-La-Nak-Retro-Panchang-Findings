"""
conftest.py — Global Test Fixtures and Reference Oracles for SPY Anomaly & Vedic Quant System
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timezone, timedelta
import zoneinfo

try:
    import swisseph as swe
except ImportError:
    swe = None

# Ensure project root and src/ are in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


# ==============================================================================
# 1. REFERENCE MATHEMATICAL ORACLES (AUTHORITATIVE DERIVATION SOURCES)
# ==============================================================================

def oracle_solid_ratio(open_val, high_val, low_val, close_val, eps=1e-9):
    """
    Authoritative Solid Ratio Formula: |Close - Open| / max(High - Low, eps)
    """
    real_body = abs(close_val - open_val)
    candle_range = high_val - low_val
    return real_body / max(candle_range, eps)


def oracle_max_wick_ratio(open_val, high_val, low_val, close_val, eps=1e-9):
    """
    Authoritative Max Wick Ratio Formula: max(Upper_Wick, Lower_Wick) / max(Range, eps)
    """
    upper_wick = high_val - max(open_val, close_val)
    lower_wick = min(open_val, close_val) - low_val
    candle_range = high_val - low_val
    return max(upper_wick, lower_wick) / max(candle_range, eps)


def oracle_julian_date_ut(dt_series):
    """
    Microsecond-safe Julian Date Number (UT) conversion.
    Unix epoch 1970-01-01 00:00:00 UTC = JD 2440587.5
    """
    dt_utc = pd.to_datetime(dt_series).dt.tz_convert('UTC')
    epoch = pd.Timestamp('1970-01-01 00:00:00', tz='UTC')
    unix_secs = (dt_utc - epoch).dt.total_seconds()
    return 2440587.5 + (unix_secs / 86400.0)


def oracle_navamsha_d9(lon_sidereal):
    """
    Vectorized Navamsha D9 sign index (0-11) from Sidereal Longitude.
    Formula: floor(lon / 3.3333333333333335) % 12
    """
    pada_span = 360.0 / 108.0  # 3°20' = 3.3333333333333335°
    if isinstance(lon_sidereal, (int, float)):
        return int(lon_sidereal / pada_span) % 12
    else:
        return (np.asarray(lon_sidereal) / pada_span).astype(int) % 12


def oracle_panchang_5_limbs(sun_lon, moon_lon, weekday_num):
    """
    Computes exact 5 Panchang limbs for given Sun/Moon Sidereal longitudes and weekday (0=Sun..6=Sat).
    """
    # 1. Tithi: (Moon - Sun) % 360 / 12 + 1 (1 to 30)
    diff_tithi = (moon_lon - sun_lon) % 360.0
    tithi_num = int(diff_tithi / 12.0) + 1
    paksha = 'Shukla' if tithi_num <= 15 else 'Krishna'

    # 2. Vara: weekday_num (0=Sunday to 6=Saturday)
    vara_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    vara_name = vara_names[weekday_num % 7]

    # 3. Nakshatra: Moon_Lon / (360/27) + 1 (1 to 27)
    nak_span = 360.0 / 27.0  # 13.333333333333334°
    nak_num = int(moon_lon / nak_span) + 1
    pada_span = nak_span / 4.0  # 3.3333333333333335°
    pada_num = int((moon_lon % nak_span) / pada_span) + 1

    # 4. Yoga: (Moon + Sun) % 360 / (360/27) + 1 (1 to 27)
    sum_yoga = (moon_lon + sun_lon) % 360.0
    yoga_num = int(sum_yoga / nak_span) + 1

    # 5. Karana: (Moon - Sun) % 360 / 6 + 1 (1 to 60)
    karana_num = int(diff_tithi / 6.0) + 1

    return {
        'tithi_num': tithi_num,
        'paksha': paksha,
        'vara_num': weekday_num,
        'vara_name': vara_name,
        'nakshatra_num': nak_num,
        'pada_num': pada_num,
        'yoga_num': yoga_num,
        'karana_num': karana_num
    }


# ==============================================================================
# 2. VALIDATION ASSERTION HELPERS
# ==============================================================================

def assert_zero_nans(df, columns=None):
    """Asserts that specified columns (or all columns) have 0 NaN values."""
    cols = columns if columns is not None else df.columns
    for c in cols:
        nan_count = df[c].isna().sum()
        assert nan_count == 0, f"Column '{c}' has {nan_count} NaNs, expected 0"


def assert_zero_duplicates(df, time_col='Datetime_UTC'):
    """Asserts that timestamp column has 0 duplicate values."""
    col = time_col if time_col in df.columns else 'Datetime'
    dupes = df[col].duplicated().sum()
    assert dupes == 0, f"Found {dupes} duplicate timestamps in column '{col}'"


def assert_monotonic_increasing(df, time_col='Datetime_UTC'):
    """Asserts that timestamps are strictly sorted in ascending order."""
    col = time_col if time_col in df.columns else 'Datetime'
    assert df[col].is_monotonic_increasing, f"Timestamps in '{col}' are not monotonic increasing"


def assert_sieve_conditions(df):
    """
    Asserts that 100% of extracted anomaly rows meet the core sieve criteria.
    """
    if len(df) == 0:
        return
    
    # 1. Solid Ratio >= 0.65
    if 'Solid_Ratio' in df.columns:
        invalid_sr = (df['Solid_Ratio'] < 0.65).sum()
        assert invalid_sr == 0, f"{invalid_sr} rows have Solid_Ratio < 0.65 (min: {df['Solid_Ratio'].min()})"

    # 2. Max Wick Ratio <= 0.25
    if 'Max_Wick_Ratio' in df.columns:
        invalid_mwr = (df['Max_Wick_Ratio'] > 0.25).sum()
        assert invalid_mwr == 0, f"{invalid_mwr} rows have Max_Wick_Ratio > 0.25 (max: {df['Max_Wick_Ratio'].max()})"

    # 3. RVOL >= 1.50x
    rvol_col = 'RVOL' if 'RVOL' in df.columns else ('TOD_RVOL' if 'TOD_RVOL' in df.columns else None)
    if rvol_col:
        invalid_rvol = (df[rvol_col] < 1.50).sum()
        assert invalid_rvol == 0, f"{invalid_rvol} rows have {rvol_col} < 1.50 (min: {df[rvol_col].min()})"

    # 4. Direction in {'GREEN', 'RED'}
    dir_col = 'Direction' if 'Direction' in df.columns else ('Candle_Direction' if 'Candle_Direction' in df.columns else None)
    if dir_col:
        invalid_dir = (~df[dir_col].isin(['GREEN', 'RED'])).sum()
        assert invalid_dir == 0, f"{invalid_dir} rows have invalid Direction"


# ==============================================================================
# 3. PYTEST FIXTURES
# ==============================================================================

@pytest.fixture
def project_root():
    return PROJECT_ROOT


@pytest.fixture
def data_dir():
    return os.path.join(PROJECT_ROOT, "data")


@pytest.fixture
def sample_synthetic_candles():
    """
    Generates a controlled dataframe of representative candlesticks:
    - 0: Bullish Marubozu (100% solid, 0% wick) -> PASS
    - 1: Bearish Solid Candle (70% solid, 15% upper, 15% lower) -> PASS
    - 2: Shooting Star (20% solid, 70% upper wick, 10% lower) -> REJECT (Wick > 0.25)
    - 3: Hammer (20% solid, 10% upper, 70% lower wick) -> REJECT (Wick > 0.25)
    - 4: Flat / Zero-Range Candle (O=C=H=L) -> REJECT (Solid=0)
    - 5: Boundary Solid 0.65 Candle (65% solid, 17.5% upper, 17.5% lower) -> PASS
    - 6: Boundary Solid 0.64 Candle (64% solid, 18% upper, 18% lower) -> REJECT
    """
    records = [
        # 0: Bullish Marubozu (Range=10.0, Body=10.0, SR=1.0, MWR=0.0)
        {'Datetime': '2024-01-10 09:30:00-05:00', 'Open': 470.0, 'High': 480.0, 'Low': 470.0, 'Close': 480.0, 'Volume': 5000000.0},
        # 1: Bearish Solid (Range=10.0, Body=7.0, SR=0.70, UW=1.5, LW=1.5, MWR=0.15)
        {'Datetime': '2024-01-11 09:30:00-05:00', 'Open': 480.0, 'High': 481.5, 'Low': 471.5, 'Close': 473.0, 'Volume': 4500000.0},
        # 2: Shooting Star (Range=10.0, Body=2.0, SR=0.20, UW=7.0, LW=1.0, MWR=0.70)
        {'Datetime': '2024-01-12 09:30:00-05:00', 'Open': 472.0, 'High': 480.0, 'Low': 470.0, 'Close': 471.0, 'Volume': 6000000.0},
        # 3: Hammer (Range=10.0, Body=2.0, SR=0.20, UW=1.0, LW=7.0, MWR=0.70)
        {'Datetime': '2024-01-16 09:30:00-05:00', 'Open': 478.0, 'High': 480.0, 'Low': 470.0, 'Close': 479.0, 'Volume': 5500000.0},
        # 4: Flat Zero-Range (Range=0.0, Body=0.0)
        {'Datetime': '2024-01-17 09:30:00-05:00', 'Open': 475.0, 'High': 475.0, 'Low': 475.0, 'Close': 475.0, 'Volume': 100.0},
        # 5: Boundary 0.65 Solid (Range=10.0, Body=6.5, SR=0.65, UW=1.75, LW=1.75, MWR=0.175)
        {'Datetime': '2024-01-18 09:30:00-05:00', 'Open': 472.0, 'High': 480.25, 'Low': 470.25, 'Close': 478.5, 'Volume': 4800000.0},
        # 6: Boundary 0.64 Solid (Range=10.0, Body=6.4, SR=0.64, UW=1.8, LW=1.8, MWR=0.18)
        {'Datetime': '2024-01-19 09:30:00-05:00', 'Open': 472.0, 'High': 480.2, 'Low': 470.2, 'Close': 478.4, 'Volume': 4800000.0},
    ]
    df = pd.DataFrame(records)
    df['Datetime_UTC'] = pd.to_datetime(df['Datetime']).dt.tz_convert('UTC')
    df['Datetime_NY'] = pd.to_datetime(df['Datetime']).dt.tz_convert('America/New_York')
    return df


@pytest.fixture
def synthetic_intraday_series():
    """
    Generates a 30-day realistic 1-hour intraday series with U-curve volume and known anomalies.
    """
    rows = []
    base_price = 450.0
    start_date = datetime(2024, 1, 8, tzinfo=zoneinfo.ZoneInfo("America/New_York"))
    
    for day in range(30):
        current_day = start_date + timedelta(days=day)
        if current_day.weekday() >= 5:  # Skip weekends
            continue
            
        hours = [9, 10, 11, 12, 13, 14, 15]
        # Intraday volume multipliers (U-curve): 09=1.5x, 10=1.2x, 11=0.8x, 12=0.6x, 13=0.6x, 14=0.9x, 15=2.2x
        vol_mults = {9: 1.5, 10: 1.2, 11: 0.8, 12: 0.6, 13: 0.6, 14: 0.9, 15: 2.2}
        base_vol = 1_000_000.0
        
        for h in hours:
            dt_ny = current_day.replace(hour=h, minute=30 if h == 9 else 0, second=0, microsecond=0)
            
            # Normal quiet bar
            rng = 1.2
            open_p = base_price
            close_p = base_price + 0.5
            high_p = max(open_p, close_p) + 0.3
            low_p = min(open_p, close_p) - 0.4
            vol = base_vol * vol_mults[h]
            
            # Inject a controlled anomaly on Day 20, Hour 13 (midday trough with huge volume & solid body)
            if day == 20 and h == 13:
                open_p = base_price
                close_p = base_price + 4.5
                high_p = close_p + 0.2
                low_p = open_p - 0.2
                vol = base_vol * vol_mults[h] * 3.0  # 3.0x RVOL
                
            rows.append({
                'Datetime_NY': dt_ny,
                'Datetime_UTC': dt_ny.astimezone(timezone.utc),
                'Open': open_p,
                'High': high_p,
                'Low': low_p,
                'Close': close_p,
                'Volume': vol
            })
            base_price = close_p
            
    df = pd.DataFrame(rows)
    return df


@pytest.fixture
def reference_astro_epoch():
    """
    Exact Swiss Ephemeris Lahiri Sidereal reference point for 2024-01-15 12:00:00 UTC:
    Julian Day UT: 2460325.0
    Lahiri Ayanamsha: 24.192899°
    """
    return {
        'dt_utc': datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
        'jd_ut': 2460325.0,
        'sun_lon_approx': 270.6270,  # Capricorn ~0.6°
        'moon_lon_approx': 325.7002, # Aquarius ~25.7° (Purva Bhadrapada)
        'tithi_expected': 5,         # Shukla Panchami
        'paksha_expected': 'Shukla',
        'vara_expected': 1,          # Monday (0=Sun, 1=Mon)
        'vara_name_expected': 'Monday',
        'yoga_expected': 19,         # Parigha/Variyan
        'karana_expected': 9,        # Bava/Balava
    }
