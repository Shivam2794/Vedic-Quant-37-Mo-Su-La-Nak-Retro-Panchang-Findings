"""
TRUE JYOTISH ENGINE: Phase 1 — Raw Ephemeris Generator
======================================================
Queries the Swiss Ephemeris (swisseph) to generate EXACT mathematical degrees
(sidereal Lahiri Ayanamsa) for all 9 Vedic planets from 2005-01-01 to 2026-12-31.
"""

import os
import pandas as pd
import numpy as np
import swisseph as swe
from datetime import datetime, timedelta

BASE_DIR = r"C:\Users\patel\Desktop\Python\Learn"
OUTPUT_FILE = os.path.join(BASE_DIR, "raw_ephemeris_2005_2026.parquet")

# ── Configuration ────────────────────────────────────────────────────────
START_DATE = "2005-01-01"
END_DATE   = "2026-12-31"

# Vedic Planets
PLANETS = {
    "Sun":     swe.SUN,
    "Moon":    swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus":   swe.VENUS,
    "Mars":    swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn":  swe.SATURN,
    "Rahu":    swe.TRUE_NODE,
}

# Set Ephemeris Path (if needed, otherwise internal)
swe.set_ephe_path(None)

# Set Ayanamsa to Lahiri (Chitra Paksha) - Industry Standard for Vedic
swe.set_sid_mode(swe.SIDM_LAHIRI)

def get_julian_day(dt):
    # swisseph expects UTC time for standard queries
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)

def generate_ephemeris():
    start = pd.to_datetime(START_DATE)
    end   = pd.to_datetime(END_DATE)
    dates = pd.date_range(start, end, freq="D")
    
    print(f"Generating exact raw degrees for {len(dates)} days...")
    
    records = []
    flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH | swe.FLG_SPEED
    
    for dt in dates:
        # Calculate exactly at 00:00 UTC
        jd = get_julian_day(dt)
        row = {"Date": dt}
        
        for name, planet_id in PLANETS.items():
            # Returns (lon, lat, dist, speed_lon, speed_lat, speed_dist)
            res = swe.calc_ut(jd, planet_id, flags)
            pos = res[0]
            lon = pos[0]
            lat = pos[1]
            speed = pos[3]
            
            row[f"{name}_lon"] = round(lon, 6)
            row[f"{name}_lat"] = round(lat, 6)
            row[f"{name}_speed"] = round(speed, 6)
            
            # Additional Vedic derivations from exact degree
            row[f"{name}_sign"] = int(lon / 30) % 12
            row[f"{name}_retro"] = 1 if speed < 0 else 0
            
        # Ketu is exactly 180 degrees opposite Rahu (True Node)
        rahu_lon = row["Rahu_lon"]
        ketu_lon = (rahu_lon + 180.0) % 360.0
        row["Ketu_lon"]   = round(ketu_lon, 6)
        row["Ketu_sign"]  = int(ketu_lon / 30) % 12
        row["Ketu_speed"] = row["Rahu_speed"]
        row["Ketu_retro"] = row["Rahu_retro"]
        
        records.append(row)
        
    df = pd.DataFrame(records)
    print(f"Engine generation complete. Shape: {df.shape}")
    
    # Save to disk
    df.to_parquet(OUTPUT_FILE, index=False)
    print(f"Saved to: {OUTPUT_FILE}")
    
    # Mathematical verification checks
    print("\n[VERIFICATION]")
    # 2008 Crash - Oct 10 2008 (VIX hit 80)
    crash_date = pd.to_datetime("2008-10-10")
    if crash_date in df["Date"].values:
        idx = df[df["Date"] == crash_date].index[0]
        saturn_lon = df.loc[idx, "Saturn_lon"]
        saturn_sign = df.loc[idx, "Saturn_sign"]
        print(f"Oct 10, 2008 -> Saturn Longitude: {saturn_lon}° (Sign: {saturn_sign} = Leo)")
        
    # Covid Crash - Mar 20 2020
    covid_date = pd.to_datetime("2020-03-20")
    if covid_date in df["Date"].values:
        idx = df[df["Date"] == covid_date].index[0]
        saturn_lon = df.loc[idx, "Saturn_lon"]
        saturn_sign = df.loc[idx, "Saturn_sign"]
        jupiter_lon = df.loc[idx, "Jupiter_lon"]
        print(f"Mar 20, 2020 -> Saturn Longitude: {saturn_lon}° (Sign: {saturn_sign} = Sagittarius/Capricorn)")
        print(f"Mar 20, 2020 -> Jupiter Longitude: {jupiter_lon}°")
        print(f"Saturn/Jupiter distance: {abs(saturn_lon - jupiter_lon):.2f}°")

if __name__ == "__main__":
    generate_ephemeris()
