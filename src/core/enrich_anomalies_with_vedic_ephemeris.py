"""
Vedic Ephemeris & Panchang Enrichment Engine for SPY Candlestick Anomalies
Branch: feat/extreme-solid-candlestick-anomalies

Calculates exact astronomical transit features for all detected anomaly timestamps:
- Sidereal Lahiri longitudes for Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu
- 27 Nakshatras & 108 Padas
- 5 Panchang Limbs: Tithi (1-30), Vara (0-6), Nakshatra (1-27), Yoga (1-27), Karana (1-60)
- Planetary Retrograde states, Combustions, and Speed tensors
"""

import os
import sys
import swisseph as swe
import numpy as np
import pandas as pd


PLANET_MAP = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mars': swe.MARS,
    'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER,
    'Venus': swe.VENUS,
    'Saturn': swe.SATURN,
    'Rahu': swe.TRUE_NODE
}

NAKSHATRA_NAMES = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
    'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

ZODIAC_SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]


def calculate_vedic_transit(dt_utc):
    """
    Computes sidereal planetary longitudes and Panchang limbs for a given UTC timestamp.
    """
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    # Calculate Julian Day UT
    year = dt_utc.year
    month = dt_utc.month
    day = dt_utc.day
    hour_float = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    
    jd = swe.julday(year, month, day, hour_float)
    
    # Flags for sidereal speed
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    positions = {}
    speeds = {}
    is_retrograde = {}
    
    for pname, pcode in PLANET_MAP.items():
        res, ret_flags = swe.calc_ut(jd, pcode, flags)
        lon = res[0] % 360.0
        spd = res[3]
        positions[pname] = lon
        speeds[pname] = spd
        is_retrograde[pname] = bool(spd < 0)
        
    # Ketu is exactly opposite Rahu
    positions['Ketu'] = (positions['Rahu'] + 180.0) % 360.0
    speeds['Ketu'] = -speeds['Rahu']
    is_retrograde['Ketu'] = True

    sun_lon = positions['Sun']
    moon_lon = positions['Moon']

    # 1. Tithi (1 to 30)
    diff_tithi = (moon_lon - sun_lon) % 360.0
    tithi = int(diff_tithi / 12.0) + 1
    paksha = 'Shukla' if tithi <= 15 else 'Krishna'
    
    # 2. Moon Nakshatra (1 to 27) & Pada (1 to 4)
    nak_span = 360.0 / 27.0  # 13.3333 degrees
    nak_idx = int(moon_lon / nak_span)
    moon_nakshatra = NAKSHATRA_NAMES[nak_idx % 27]
    pada_span = nak_span / 4.0 # 3.3333 degrees
    moon_pada = int((moon_lon % nak_span) / pada_span) + 1
    
    # 3. Sun Nakshatra
    sun_nak_idx = int(sun_lon / nak_span)
    sun_nakshatra = NAKSHATRA_NAMES[sun_nak_idx % 27]

    # 4. Yoga (1 to 27)
    yoga_deg = (moon_lon + sun_lon) % 360.0
    yoga = int(yoga_deg / nak_span) + 1
    
    # 5. Karana (1 to 60)
    karana = int(diff_tithi / 6.0) + 1

    # 6. Zodiac Sign Placement (Rasi)
    moon_sign_idx = int(moon_lon / 30.0)
    moon_sign = ZODIAC_SIGNS[moon_sign_idx % 12]
    sun_sign_idx = int(sun_lon / 30.0)
    sun_sign = ZODIAC_SIGNS[sun_sign_idx % 12]

    # 7. Navamsha Sign (D9)
    navamsha_span = 30.0 / 9.0  # 3.3333 degrees
    moon_d9_idx = int(moon_lon / navamsha_span) % 12
    moon_d9_sign = ZODIAC_SIGNS[moon_d9_idx]

    # 8. Combustion Checks (Within standard classical orbs)
    combustion_orbs = {'Mars': 17.0, 'Mercury': 14.0, 'Jupiter': 11.0, 'Venus': 10.0, 'Saturn': 15.0}
    is_combust = {}
    for p, orb in combustion_orbs.items():
        sep = abs((positions[p] - sun_lon + 180.0) % 360.0 - 180.0)
        is_combust[f"{p}_Combust"] = bool(sep <= orb)

    record = {
        'Julian_Day': jd,
        'Moon_Longitude': moon_lon,
        'Sun_Longitude': sun_lon,
        'Mars_Longitude': positions['Mars'],
        'Mercury_Longitude': positions['Mercury'],
        'Jupiter_Longitude': positions['Jupiter'],
        'Venus_Longitude': positions['Venus'],
        'Saturn_Longitude': positions['Saturn'],
        'Rahu_Longitude': positions['Rahu'],
        'Ketu_Longitude': positions['Ketu'],
        'Tithi': tithi,
        'Paksha': paksha,
        'Moon_Nakshatra': moon_nakshatra,
        'Moon_Pada': moon_pada,
        'Sun_Nakshatra': sun_nakshatra,
        'Yoga': yoga,
        'Karana': karana,
        'Moon_Sign': moon_sign,
        'Sun_Sign': sun_sign,
        'Moon_D9_Sign': moon_d9_sign,
        'Mercury_Retrograde': is_retrograde['Mercury'],
        'Mars_Retrograde': is_retrograde['Mars'],
        'Jupiter_Retrograde': is_retrograde['Jupiter'],
        'Saturn_Retrograde': is_retrograde['Saturn'],
        'Venus_Retrograde': is_retrograde['Venus'],
    }
    record.update(is_combust)
    return record


def enrich_master_anomalies():
    repo_root = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\Vedic-Quant-37-Mo-Su-La-Nak-Retro-Panchang-Findings"
    data_dir = os.path.join(repo_root, "data")
    
    master_parquet = os.path.join(data_dir, "spy_anomalies_master_manifest.parquet")
    if not os.path.exists(master_parquet):
        raise FileNotFoundError(f"Master manifest not found at {master_parquet}")
        
    print(f"Loading Master Manifest from {master_parquet}...")
    df = pd.read_parquet(master_parquet)
    print(f"Loaded {len(df)} total anomaly candlesticks.")
    
    dt_col = 'Datetime_UTC' if 'Datetime_UTC' in df.columns else 'Datetime'
    utc_series = pd.to_datetime(df[dt_col]).dt.tz_convert('UTC')
    
    print("Computing Vedic Planetary Positions and Panchang Limbs via Swiss Ephemeris...")
    enriched_records = []
    for idx, dt_utc in enumerate(utc_series):
        if idx % 500 == 0:
            print(f"  Processed {idx}/{len(df)} timestamps...", flush=True)
        rec = calculate_vedic_transit(dt_utc)
        enriched_records.append(rec)
        
    df_vedic = pd.DataFrame(enriched_records)
    df_combined = pd.concat([df.reset_index(drop=True), df_vedic.reset_index(drop=True)], axis=1)
    
    out_parquet = os.path.join(data_dir, "spy_anomalies_vedic_enriched.parquet")
    out_csv = os.path.join(data_dir, "spy_anomalies_vedic_enriched.csv")
    
    df_combined.to_parquet(out_parquet, index=False)
    df_combined.to_csv(out_csv, index=False)
    
    print("================================================================================")
    print("  VEDIC ASTROLOGICAL ENRICHMENT COMPLETE")
    print(f"  Saved Enriched Parquet: {out_parquet} ({os.path.getsize(out_parquet):,} bytes)")
    print(f"  Saved Enriched CSV    : {out_csv} ({os.path.getsize(out_csv):,} bytes)")
    print(f"  Total Features        : {df_combined.shape[1]} columns across {len(df_combined)} anomalies")
    print("================================================================================")
    
    return df_combined


if __name__ == "__main__":
    enrich_master_anomalies()
