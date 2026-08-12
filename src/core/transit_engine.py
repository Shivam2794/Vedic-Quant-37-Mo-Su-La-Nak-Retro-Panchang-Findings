"""
Transit & Dasha Engine — Layer 2 & 3 of the Astrological Compiler
================================================================
Takes the universal sky state (from ephemeris_engine.py) and a stock's
natal chart (from stock_natal_charts.db) to compute the TRUE predictive
features: Transit-Over-Natal aspects, transits through natal houses, 
and the current Dasha state for that specific stock.
"""
import sqlite3
import json
import math
from datetime import datetime, timezone
import numpy as np
import swisseph as swe

# Import universal features
from ephemeris_engine import (
    compute_all_features, angular_distance, forward_distance,
    aspect_strength, dt_to_jd, BODIES, PARASHARI_SPECIAL, SIGN_LORDS
)

DB_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_natal_charts.db"

VIM_LORDS = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
VIM_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]
VIM_DAYS = [y * 365.25636042 for y in VIM_YEARS]

# Standard aspect angles/orbs
ASPECT_ANGLES = [0, 60, 90, 120, 180]
ASPECT_NAMES = ["conj", "sext", "sqr", "tri", "opp"]
ASPECT_ORBS = [8, 6, 8, 8, 8]

ALL_PLANET_NAMES = [n for _, n in BODIES] + ["Rahu", "Ketu"]


class StockAstroEngine:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.c = self.conn.cursor()
        
        # Cache natal charts to avoid DB hits during backtest
        self.natal_cache = {}
        self._load_all_natal_charts()
        
    def _load_all_natal_charts(self):
        self.c.execute("SELECT ticker, ipo_date, natal_chart_json, moon_nakshatra FROM stocks")
        rows = self.c.fetchall()
        for row in rows:
            ticker, ipo_date, natal_json, moon_nak = row
            if natal_json:
                natal = json.loads(natal_json)
                self.natal_cache[ticker] = {
                    "ipo_date": ipo_date,
                    "natal": natal,
                    "moon_nak": moon_nak
                }
        print(f"Loaded {len(self.natal_cache)} natal charts into memory.")

    def compute_stock_features(self, dt: datetime, ticker: str, sky_state: dict = None) -> dict:
        """
        Compute stock-specific astro features for a given time.
        If sky_state is not provided, it will be computed.
        """
        if ticker not in self.natal_cache:
            raise ValueError(f"Ticker {ticker} not found in natal database.")
            
        natal_data = self.natal_cache[ticker]["natal"]
        ipo_date_str = self.natal_cache[ticker]["ipo_date"]
        
        # 1. Get universal sky state
        if sky_state is None:
            sky_state = compute_all_features(dt)
            
        features = {}
        
        # Extract transit longitudes from sky_state
        transit_lons = {p: sky_state[f"{p}_longitude"] for p in ALL_PLANET_NAMES if f"{p}_longitude" in sky_state}
        transit_speeds = {p: sky_state.get(f"{p}_speed", 0) for p in ALL_PLANET_NAMES}
        
        natal_planets = natal_data.get("planets", {})
        
        # ════════════════════════════════════════
        # LAYER 2A: TRANSIT-OVER-NATAL ASPECTS
        # ════════════════════════════════════════
        for t_name, t_lon in transit_lons.items():
            for n_name, n_data in natal_planets.items():
                n_lon = n_data.get("longitude", 0)
                
                ang_dist = angular_distance(t_lon, n_lon)
                prefix = f"ton_{t_name}_{n_name}" # ton = Transit Over Natal
                
                features[f"{prefix}_dist"] = ang_dist
                
                # Check each aspect type
                for a_angle, a_name, a_orb in zip(ASPECT_ANGLES, ASPECT_NAMES, ASPECT_ORBS):
                    strength = aspect_strength(ang_dist, a_angle, a_orb)
                    features[f"{prefix}_{a_name}"] = strength

        # ════════════════════════════════════════
        # LAYER 2B: TRANSITS THROUGH NATAL HOUSES
        # ════════════════════════════════════════
        natal_houses = natal_data.get("houses", {})
        if natal_houses:
            cusps = [natal_houses[f"house_{i+1}"] for i in range(12)]
            for t_name, t_lon in transit_lons.items():
                house_idx = 0
                for h in range(12):
                    next_h = (h + 1) % 12
                    cusp1 = cusps[h]
                    cusp2 = cusps[next_h]
                    if cusp2 < cusp1:
                        cusp2 += 360
                    p_check = t_lon if t_lon >= cusp1 else t_lon + 360
                    if cusp1 <= p_check < cusp2:
                        house_idx = h + 1
                        break
                features[f"transit_{t_name}_in_natal_house"] = house_idx

        # ════════════════════════════════════════
        # LAYER 2C: SPECIAL PATTERNS (Sade Sati, etc.)
        # ════════════════════════════════════════
        if "Moon" in natal_planets and "Saturn" in transit_lons:
            n_moon = natal_planets["Moon"]["longitude"]
            t_saturn = transit_lons["Saturn"]
            dist_sat_moon = (t_saturn - n_moon) % 360
            
            # Sade Sati: Saturn within 45 degrees before to 45 degrees after natal Moon
            # Actually, traditional is 1 sign before, moon sign, 1 sign after (roughly 90 degrees total)
            sade_sati_active = 1.0 if (dist_sat_moon >= 315 or dist_sat_moon <= 45) else 0.0
            features["sade_sati_active"] = sade_sati_active
            
        if "Moon" in natal_planets and "Rahu" in transit_lons:
            n_moon = natal_planets["Moon"]["longitude"]
            t_rahu = transit_lons["Rahu"]
            features["rahu_over_natal_moon"] = aspect_strength(angular_distance(t_rahu, n_moon), 0, 10.0)

        # ════════════════════════════════════════
        # LAYER 2D: PARASHARI TRANSIT-OVER-NATAL ASPECTS
        # ════════════════════════════════════════
        # Which transit planets project special aspects onto natal planets?
        parashari_pids = { "Mars": swe.MARS, "Jupiter": swe.JUPITER, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE }
        for t_name, pid in parashari_pids.items():
            if t_name not in transit_lons: continue
            t_lon = transit_lons[t_name]
            for special_house in PARASHARI_SPECIAL[pid]:
                target_angle = (special_house - 1) * 30
                for n_name, n_data in natal_planets.items():
                    n_lon = n_data.get("longitude", 0)
                    f_dist = forward_distance(t_lon, n_lon)
                    strength = aspect_strength(f_dist, target_angle, 10.0)
                    features[f"ton_{t_name}_parashari_{special_house}th_{n_name}"] = strength

        # ════════════════════════════════════════
        # LAYER 2E: GENUINE YOGAS (TRANSIT)
        # ════════════════════════════════════════
        # Guru-Chandal Yoga (Jupiter + Rahu conjunct in transit)
        if "Jupiter" in transit_lons and "Rahu" in transit_lons:
            dist = angular_distance(transit_lons["Jupiter"], transit_lons["Rahu"])
            features["yoga_guru_chandal"] = aspect_strength(dist, 0, 10.0)
            
        # Angarak Yoga (Mars + Rahu/Ketu conjunct)
        if "Mars" in transit_lons and "Rahu" in transit_lons:
            dist_r = angular_distance(transit_lons["Mars"], transit_lons["Rahu"])
            dist_k = angular_distance(transit_lons["Mars"], transit_lons["Ketu"])
            features["yoga_angarak"] = max(aspect_strength(dist_r, 0, 10.0), aspect_strength(dist_k, 0, 10.0))
            
        # Grahan Dosha (Eclipse: Sun/Moon conjunct Nodes)
        if "Sun" in transit_lons and "Rahu" in transit_lons and "Moon" in transit_lons:
            sun_r = aspect_strength(angular_distance(transit_lons["Sun"], transit_lons["Rahu"]), 0, 10.0)
            sun_k = aspect_strength(angular_distance(transit_lons["Sun"], transit_lons["Ketu"]), 0, 10.0)
            moon_r = aspect_strength(angular_distance(transit_lons["Moon"], transit_lons["Rahu"]), 0, 10.0)
            moon_k = aspect_strength(angular_distance(transit_lons["Moon"], transit_lons["Ketu"]), 0, 10.0)
            features["yoga_grahan_sun"] = max(sun_r, sun_k)
            features["yoga_grahan_moon"] = max(moon_r, moon_k)
            
        # Kemadruma Yoga approximation (Transit Moon isolated from other transiting planets)
        if "Moon" in transit_lons:
            moon_lon = transit_lons["Moon"]
            isolated = 1.0
            for p in ALL_PLANET_NAMES:
                if p in ("Moon", "Sun", "Rahu", "Ketu"): continue
                if p not in transit_lons: continue
                # Is planet in 2nd or 12th sign from Moon? (Within ~30 to 60 deg or 300 to 330 deg)
                f_dist = forward_distance(moon_lon, transit_lons[p])
                # Check adjacent houses (simplified as 30 to 60, or 300 to 330 distance)
                if (30 <= f_dist <= 60) or (300 <= f_dist <= 330):
                    isolated = 0.0
                    break
            features["yoga_kemadruma"] = isolated

        # ════════════════════════════════════════
        # LAYER 3: VIMSHOTTARI DASHA (Exact calculation)
        # ════════════════════════════════════════
        moon_nak = self.natal_cache[ticker]["moon_nak"]
        starting_lord_idx = moon_nak % 9
        
        moon_lon = natal_planets["Moon"]["longitude"]
        nak_start = moon_nak * (360 / 27)
        elapsed_fraction = (moon_lon - nak_start) / (360 / 27)
        first_dasha_elapsed = elapsed_fraction * VIM_DAYS[starting_lord_idx]
        
        ipo_parts = ipo_date_str.split("-")
        ipo_dt = datetime(int(ipo_parts[0]), int(ipo_parts[1]), int(ipo_parts[2]), tzinfo=timezone.utc)
        
        # Fix dt to be UTC aware if not
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
            
        days_since_ipo = (dt - ipo_dt).days
        total_cycle_days = sum(VIM_DAYS)
        
        # If before IPO, zero out dashas
        if days_since_ipo < 0:
            for i in range(9):
                features[f"dasha_{VIM_LORDS[i]}"] = 0.0
            features["dasha_mahadasha_pct"] = 0.0
        else:
            days_in_cycle = (days_since_ipo + first_dasha_elapsed) % total_cycle_days
            cumulative = 0
            
            # One-hot encode the current Mahadasha lord
            for i in range(9):
                features[f"dasha_{VIM_LORDS[i]}"] = 0.0
                
            for i in range(9):
                lord_idx = (starting_lord_idx + i) % 9
                period_days = VIM_DAYS[lord_idx]
                if cumulative + period_days > days_in_cycle:
                    current_lord = VIM_LORDS[lord_idx]
                    features[f"dasha_{current_lord}"] = 1.0
                    features["dasha_mahadasha_pct"] = (days_in_cycle - cumulative) / period_days
                    break
                cumulative += period_days
                
        return features

if __name__ == "__main__":
    import time
    
    print("Initializing Stock Astro Engine...")
    engine = StockAstroEngine()
    
    # Test AAPL
    dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    print("\nComputing universal sky state for 2024-01-01...")
    sky = compute_all_features(dt)
    
    print("\nComputing AAPL transit & dasha features...")
    t0 = time.perf_counter()
    aapl_features = engine.compute_stock_features(dt, "AAPL", sky)
    t1 = time.perf_counter()
    
    print(f"Computed {len(aapl_features)} stock-specific features in {(t1-t0)*1000:.2f} ms")
    
    print("\nSample Features:")
    # Show aspects to Natal Jupiter
    for k, v in aapl_features.items():
        if "ton_Saturn_Jupiter" in k:
            print(f"  {k:30s} : {v:.4f}")
            
    print(f"  {'sade_sati_active':30s} : {aapl_features.get('sade_sati_active', 0)}")
    
    print("\nCurrent Dasha (One-hot encoded):")
    for k, v in aapl_features.items():
        if k.startswith("dasha_") and v > 0:
            print(f"  {k:30s} : {v:.4f}")
            
    # Benchmark full matrix generation (Sky + 500 stocks)
    print("\nBenchmarking Matrix Generation for 1 timestamp (500 stocks)...")
    tickers = list(engine.natal_cache.keys())[:500]
    
    t_start = time.perf_counter()
    sky_state = compute_all_features(dt)
    all_stock_features = {}
    for tk in tickers:
        all_stock_features[tk] = engine.compute_stock_features(dt, tk, sky_state)
    t_end = time.perf_counter()
    
    total_time = t_end - t_start
    print(f"Generated complete feature vector for {len(tickers)} stocks in {total_time*1000:.1f} ms")
    print(f"Total features per stock: {len(sky_state) + len(aapl_features)}")
    print(f"Estimated time to generate 10 years of daily data (2520 bars): {total_time * 2520:.1f} seconds")
