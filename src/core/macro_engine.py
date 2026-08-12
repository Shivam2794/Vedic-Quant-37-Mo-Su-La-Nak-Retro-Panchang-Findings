"""
Phase 6D: Mundane Astrology Feature Engine (Macro Assets)
=========================================================
Generates the feature matrix for macro assets (SPY, QQQ, Gold, Silver, Copper)
using Mundane Astrology (continuous sky state) instead of Natal Dashas,
since indexes and commodities do not have birth dates.
"""
import yfinance as yf
import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import swisseph as swe
from datetime import datetime, timezone
import os

MARKET_DATA_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\market_data"
OUTPUT_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\macro_features_partitioned"

MACRO_ASSETS = {
    "SPY": "SPY",         # S&P 500 ETF
    "QQQ": "QQQ",         # Nasdaq 100 ETF
    "XAUUSD": "GC=F",     # Gold Futures (proxy for XAUUSD)
    "XAGUSD": "SI=F",     # Silver Futures
    "COPPER": "HG=F",     # Copper Futures
}

# ─── Ephemeris Logic (Mundane) ───
swe.set_sid_mode(swe.SIDM_LAHIRI)

def compute_mundane_sky(dt_utc):
    """Computes Mundane features (no natal reference) for a specific datetime."""
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, 14.5)  # 9:30 AM ET
    
    planets = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
        "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO
    }
    
    features = {}
    ayanamsa = swe.get_ayanamsa(jd)
    
    # 1. Planetary Positions, Speeds, Declinations
    positions = {}
    for name, pid in planets.items():
        # Ecliptic coordinates (longitude, latitude, distance, speed in long, speed in lat, speed in dist)
        pos = swe.calc_ut(jd, pid)
        lon_tropical = pos[0][0]
        lon_sidereal = (lon_tropical - ayanamsa) % 360
        speed = pos[0][3]
        
        # Equatorial coordinates for Declination
        equat = swe.calc_ut(jd, pid, swe.FLG_EQUATORIAL | swe.FLG_SWIEPH)
        declination = equat[0][1]
        
        positions[name] = lon_sidereal
        
        features[f"{name}_speed"] = speed
        features[f"{name}_retrograde"] = 1.0 if speed < 0 else 0.0
        features[f"{name}_declination"] = declination
        features[f"{name}_lon_sin"] = np.sin(np.radians(lon_sidereal))
        features[f"{name}_lon_cos"] = np.cos(np.radians(lon_sidereal))
        
        # Ingress (Sign changes) - categorical represented as cyclics
        sign_idx = int(lon_sidereal / 30)
        features[f"{name}_sign_sin"] = np.sin(sign_idx * (np.pi / 6))
        features[f"{name}_sign_cos"] = np.cos(sign_idx * (np.pi / 6))

    # Rahu / Ketu (Mean Nodes)
    rahu_pos = swe.calc_ut(jd, swe.MEAN_NODE)
    rahu_lon = (rahu_pos[0][0] - ayanamsa) % 360
    ketu_lon = (rahu_lon + 180) % 360
    
    positions["Rahu"] = rahu_lon
    positions["Ketu"] = ketu_lon
    
    features["Rahu_lon_sin"] = np.sin(np.radians(rahu_lon))
    features["Rahu_lon_cos"] = np.cos(np.radians(rahu_lon))
    features["Ketu_lon_sin"] = np.sin(np.radians(ketu_lon))
    features["Ketu_lon_cos"] = np.cos(np.radians(ketu_lon))

    # 2. Key Mundane Aspects (Distances)
    pairs = [
        ("Jupiter", "Saturn"), ("Saturn", "Uranus"), ("Saturn", "Pluto"),
        ("Uranus", "Pluto"), ("Jupiter", "Pluto"), ("Mars", "Saturn"),
        ("Sun", "Rahu"), ("Moon", "Rahu")
    ]
    
    for p1, p2 in pairs:
        dist = abs(positions[p1] - positions[p2])
        dist = min(dist, 360 - dist)
        features[f"aspect_{p1}_{p2}_dist"] = dist
        features[f"aspect_{p1}_{p2}_sin"] = np.sin(np.radians(dist))
        features[f"aspect_{p1}_{p2}_cos"] = np.cos(np.radians(dist))
        
    # 3. Moon Phase
    moon_phase = (positions["Moon"] - positions["Sun"]) % 360
    features["Moon_phase"] = moon_phase
    features["Moon_phase_sin"] = np.sin(np.radians(moon_phase))
    features["Moon_phase_cos"] = np.cos(np.radians(moon_phase))
    
    return features

def download_and_process_macro(name, symbol, sky_cache):
    print(f"Processing Macro Asset: {name} ({symbol})")
    
    # 1. Download Data
    df = yf.download(symbol, period="max", progress=False, auto_adjust=True)
    if len(df) == 0:
        print(f"  ERROR: No data for {symbol}")
        return
    
    df = df.reset_index()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if c[1] == '' or c[1] == symbol else c[0] for c in df.columns]
        
    # Standardize cols
    col_map = {c: c.capitalize() if c.lower() != 'date' else 'Date' for c in df.columns}
    df = df.rename(columns=col_map)
    
    # Forward Returns
    for days in [1, 5, 10, 21, 63]:
        df[f"fwd_return_{days}d"] = df['Close'].pct_change(periods=days).shift(-days)
        
    df = df.dropna(subset=[f"fwd_return_{d}d" for d in [1, 5, 10, 21, 63]])
    
    # 2. Build Feature Matrix
    all_rows = []
    for _, row in df.iterrows():
        dt = row['Date']
        dt_utc = datetime(dt.year, dt.month, dt.day, 14, 30, tzinfo=timezone.utc)
        date_str = dt_utc.strftime("%Y-%m-%d")
        
        if date_str not in sky_cache:
            sky_cache[date_str] = compute_mundane_sky(dt_utc)
            
        sky_features = sky_cache[date_str]
        
        combined = {
            "date": dt_utc,
            "ticker": name,
            "open": row["Open"],
            "high": row["High"],
            "low": row["Low"],
            "close": row["Close"],
            "volume": row["Volume"] if "Volume" in row else 0,
            **{f"fwd_return_{d}d": row[f"fwd_return_{d}d"] for d in [1, 5, 10, 21, 63]},
            **sky_features
        }
        all_rows.append(combined)
        
    feat_df = pd.DataFrame(all_rows)
    feat_df['year'] = feat_df['date'].dt.year
    
    # 3. Save
    table = pa.Table.from_pandas(feat_df)
    pq.write_to_dataset(table, root_path=OUTPUT_DIR, partition_cols=['ticker', 'year'])
    print(f"  -> Generated {len(feat_df)} rows for {name}")

def main():
    print("=" * 60)
    print("PHASE 6D: MACRO ASSET GENERATOR")
    print("=" * 60)
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    sky_cache = {}
    for name, symbol in MACRO_ASSETS.items():
        download_and_process_macro(name, symbol, sky_cache)

if __name__ == "__main__":
    main()
