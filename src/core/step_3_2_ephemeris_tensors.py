
"""
STEP 3.2 & 3.3: THE SEALED EPHEMERIS TENSOR FACTORY (V3)

Traps Addressed in this file:
  - Traps 3.2.1 to 3.2.11 (Ascendant Crash, Acceleration, True/Mean Nodes, etc.)
  - TRAP 3.3.A: Helio Retrograde           -> Explicit Helio_Is_Retrograde = 0
  - TRAP 3.3.B: Helio Sidereal             -> Added Lon_Sidereal to Helio tensor
  - TRAP 3.3.C: Helio Acceleration         -> Post-loop np.diff on Helio speed
  - TRAP 3.3.D: Helio Earth                -> Added Earth (Sun_Topo + 180) to Helio
  - TRAP 3.3.E/F: Indu/Shree Lagna         -> Removed. Deferred to post-Step 3.8
  - TRAP 3.3.G: Gulika DOW                 -> Remapped: 0=Sunday, 1=Monday
  - TRAP 3.3.H: Helio Parquet              -> Explicitly written to disk
  - TRAP 3.3.I: Mandi                      -> Derived from night table
  - TRAP 3.3.J: Upagraha Exception         -> Counter + Warning
  - TRAP 3.3.L: Helio Midnight JD          -> Sweep runs on jd_midnight
  - TRAP 3.2.N1: Hora Lagna                -> Uses Sunrise Ascendant & 30 deg/hr
  - TRAP 3.2.N3: Asc/Ketu Acceleration     -> Ketu = Rahu accel, Asc/MC = 0
  - TRAP 3.2.N4: Vectorized Ayanamsha      -> Pre-computed outside the loop
  - TRAP 3.2.N5: Node Declination          -> Equatorial pass extended to True/Mean nodes

Author: Sealed Engine V3
"""

import numpy as np
import swisseph as swe
import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# ─── Constants ────────────────────────────────────────────────────────────────
OUTPUT_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\master_output"
EPHE_PATH  = r"C:\ephemeris"

# Wall Street exact coordinates (NYSE, 11 Wall St, New York)
WST_LON = -74.0113
WST_LAT = 40.7069
WST_ALT = 10.0

# Topocentric entities (16 total)
PLANET_IDS = [
    swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, swe.VENUS, swe.SATURN,
    swe.URANUS, swe.NEPTUNE, swe.PLUTO, swe.TRUE_NODE, swe.MEAN_NODE,
]
PLANET_NAMES = [
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
    "Uranus", "Neptune", "Pluto", "Rahu_True", "Rahu_Mean",
    "Ketu_True", "Ketu_Mean", "Ascendant", "MC"
]
N_ENTITIES = len(PLANET_NAMES)

NODE_INDICES = {10, 11, 12, 13}
ASC_MC_INDICES = {14, 15}

# Heliocentric entities (9 total, TRAP 3.3.D FIX)
HELIO_PLANET_IDS = [swe.MARS, swe.MERCURY, swe.JUPITER, swe.VENUS,
                    swe.SATURN, swe.URANUS, swe.NEPTUNE, swe.PLUTO]
HELIO_NAMES = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Uranus", "Neptune", "Pluto", "Earth"]
N_HELIO = len(HELIO_NAMES)

# Flag chains
TOPO_FLAGS_TROPICAL   = swe.FLG_SWIEPH | swe.FLG_SPEED
TOPO_FLAGS_EQUATORIAL = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_EQUATORIAL
HELIO_FLAGS_TROPICAL  = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_HELCTR
HOUSES_FLAGS          = swe.FLG_SWIEPH


def _derive_ketu(rahu_lon, rahu_lat, rahu_dist, rahu_speed):
    ketu_lon  = (rahu_lon + 180.0) % 360.0
    ketu_lat  = -rahu_lat
    ketu_dist = rahu_dist
    ketu_speed = rahu_speed
    return ketu_lon, ketu_lat, ketu_dist, ketu_speed


def _derive_upagrahas(jd_ut, lat, lon):
    # Sunrise & Sunset
    geopos = [lon, lat, WST_ALT]
    try:
        _, tret = swe.rise_trans(jd_ut - 0.5, swe.SUN, geopos, rsmi=swe.CALC_RISE, atpress=1013.25, attemp=15)
        sunrise_jd = tret[0]
    except Exception:
        sunrise_jd = jd_ut - 0.25
    try:
        _, tret2 = swe.rise_trans(jd_ut - 0.5, swe.SUN, geopos, rsmi=swe.CALC_SET, atpress=1013.25, attemp=15)
        sunset_jd = tret2[0]
    except Exception:
        sunset_jd = jd_ut + 0.25

    day_length_jd = sunset_jd - sunrise_jd
    night_length_jd = 1.0 - day_length_jd # Approx

    # TRAP 3.3.G FIX: DOW mapping
    dow_adj = int(jd_ut + 1.5 + 6) % 7 # 0=Sunday
    
    gulika_table_day   = [6, 5, 4, 3, 2, 1, 0]
    gulika_table_night = [3, 2, 1, 0, 6, 5, 4]

    # Gulika (Day)
    gulika_frac_day = gulika_table_day[dow_adj] / 8.0
    gulika_jd = sunrise_jd + gulika_frac_day * day_length_jd
    g_cusps, g_ascmc = swe.houses_ex(gulika_jd, lat, lon, b'P', HOUSES_FLAGS)
    gulika_lon = g_ascmc[0]
    
    # Mandi (Night) - TRAP 3.3.I FIX
    mandi_frac_night = gulika_table_night[dow_adj] / 8.0
    mandi_jd = sunset_jd + mandi_frac_night * night_length_jd
    m_cusps, m_ascmc = swe.houses_ex(mandi_jd, lat, lon, b'P', HOUSES_FLAGS)
    mandi_lon = m_ascmc[0]

    # Hora Lagna - TRAP 3.2.N1 FIX
    _, sunrise_ascmc = swe.houses_ex(sunrise_jd, lat, lon, b'P', HOUSES_FLAGS)
    sunrise_asc = sunrise_ascmc[0]
    elapsed_hours = (jd_ut - sunrise_jd) * 24.0
    hora_lagna = (sunrise_asc + elapsed_hours * 30.0) % 360.0

    # Bhrigu Bindu
    swe.set_sid_mode(swe.SIDM_LAHIRI)  # CRITICAL BUG FIX #5: Moved before calc
    moon_pos, _ = swe.calc_ut(float(jd_ut), swe.MOON, TOPO_FLAGS_TROPICAL)
    rahu_pos, _ = swe.calc_ut(float(jd_ut), swe.TRUE_NODE, TOPO_FLAGS_TROPICAL)
    moon_lon = moon_pos[0]
    rahu_lon = rahu_pos[0]
    bhrigu_bindu = ((moon_lon + rahu_lon) / 2.0) % 360.0

    return {
        "Gulika_Lon": gulika_lon,
        "Mandi_Lon": mandi_lon,
        "Hora_Lagna_Lon": hora_lagna,
        "Bhrigu_Bindu_Lon": bhrigu_bindu,
    }


def execute_step_3_2():
    print("=" * 60)
    print("STEP 3.2 & 3.3: SEALED EPHEMERIS TENSOR FACTORY (V3)")
    print("=" * 60)

    swe.set_ephe_path(EPHE_PATH)
    swe.set_topo(WST_LON, WST_LAT, WST_ALT)

    jd_file = os.path.join(OUTPUT_DIR, "SPY_jd_index.npy")
    jd_array = np.load(jd_file)
    N = len(jd_array)
    
    # TRAP 3.3.L FIX: Helio Midnight JD
    jd_midnight_array = np.floor(jd_array - 0.5) + 0.5

    # TRAP 3.2.N4 FIX: Precompute Ayanamshas
    print("Pre-computing Ayanamshas...")
    lahiri_ayanamsha_arr = np.array([swe.get_ayanamsa_ut(float(jd)) for jd in jd_array])
    kp_ayanamsha_arr = np.array([swe.get_ayanamsa_ut(float(jd)) for jd in jd_array])

    # Tensors
    N_FIELDS = 8
    topo_tensor  = np.full((N, N_ENTITIES, N_FIELDS), np.nan, dtype=np.float64)
    # Helio fields: Lon, Lat, Dist, Speed, Lon_Sidereal, Acceleration (TRAP 3.3.B, 3.3.C)
    N_HELIO_FIELDS = 6
    helio_tensor = np.full((N, N_HELIO, N_HELIO_FIELDS), np.nan, dtype=np.float64)

    upagraha_names  = ["Gulika_Lon", "Mandi_Lon", "Hora_Lagna_Lon", "Bhrigu_Bindu_Lon"]
    upagraha_matrix = np.full((N, len(upagraha_names)), np.nan, dtype=np.float64)

    fail_count = 0 # TRAP 3.3.J FIX

    print("Executing C-Sweeps (Topocentric & Heliocentric passes)...")

    for i in range(N):
        jd_f = float(jd_array[i])
        jd_h = float(jd_midnight_array[i])
        
        # ── Pass 1: Topo Tropical ─────────────
        for j, pid in enumerate(PLANET_IDS):
            pos, _ = swe.calc_ut(jd_f, pid, TOPO_FLAGS_TROPICAL)
            topo_tensor[i, j, 0] = pos[0]
            topo_tensor[i, j, 1] = pos[1]
            if j in NODE_INDICES or pid in (swe.TRUE_NODE, swe.MEAN_NODE):
                topo_tensor[i, j, 2] = np.nan
            else:
                topo_tensor[i, j, 2] = pos[2]
            topo_tensor[i, j, 3] = pos[3]

        # ── Derive Ketu ─────────────────────────
        for rahu_idx, ketu_idx in [(10, 12), (11, 13)]:
            kl, klat, kdist, kspd = _derive_ketu(
                topo_tensor[i, rahu_idx, 0], topo_tensor[i, rahu_idx, 1],
                topo_tensor[i, rahu_idx, 2], topo_tensor[i, rahu_idx, 3]
            )
            topo_tensor[i, ketu_idx, 0] = kl
            topo_tensor[i, ketu_idx, 1] = klat
            topo_tensor[i, ketu_idx, 2] = np.nan
            topo_tensor[i, ketu_idx, 3] = kspd

        # ── Ascendant & MC ────────
        cusps, ascmc = swe.houses_ex(jd_f, WST_LAT, WST_LON, b'P', HOUSES_FLAGS)
        topo_tensor[i, 14, 0] = ascmc[0] # Tropical Asc/MC (Sidereal derived in field 6)
        topo_tensor[i, 15, 0] = ascmc[1]
        topo_tensor[i, 14, 3] = 360.0
        topo_tensor[i, 15, 3] = 360.0

        # ── Pass 2: Topo Equatorial (TRAP 3.2.N5 FIX: Include Nodes) ─
        for j, pid in enumerate(PLANET_IDS):
            pos_eq, _ = swe.calc_ut(jd_f, pid, TOPO_FLAGS_EQUATORIAL)
            topo_tensor[i, j, 4] = pos_eq[1]   # Declination
            topo_tensor[i, j, 5] = pos_eq[0]   # RA

        # Ketu Declination = -Rahu Declination
        topo_tensor[i, 12, 4] = -topo_tensor[i, 10, 4]
        topo_tensor[i, 12, 5] = (topo_tensor[i, 10, 5] + 180.0) % 360.0
        topo_tensor[i, 13, 4] = -topo_tensor[i, 11, 4]
        topo_tensor[i, 13, 5] = (topo_tensor[i, 11, 5] + 180.0) % 360.0

        # ── Topo Sidereal Longitude ─
        topo_tensor[i, :, 6] = (topo_tensor[i, :, 0] - lahiri_ayanamsha_arr[i]) % 360.0

        # ── Heliocentric Pass ─
        for j, pid in enumerate(HELIO_PLANET_IDS):
            pos_h, _ = swe.calc_ut(jd_h, pid, HELIO_FLAGS_TROPICAL)
            helio_tensor[i, j, 0] = pos_h[0]
            helio_tensor[i, j, 1] = pos_h[1]
            helio_tensor[i, j, 2] = pos_h[2]
            helio_tensor[i, j, 3] = pos_h[3]
            helio_tensor[i, j, 4] = (pos_h[0] - lahiri_ayanamsha_arr[i]) % 360.0
            
        # ── Earth Helio (TRAP 3.3.D FIX) ─
        # Note: Earth Helio Lon uses the topo Sun Tropical Lon for exact corresponding time, not midnight.
        # But to be precise to midnight, we should calc Sun topo at jd_h.
        sun_h, _ = swe.calc_ut(jd_h, swe.SUN, TOPO_FLAGS_TROPICAL)
        helio_tensor[i, 8, 0] = (sun_h[0] + 180.0) % 360.0
        helio_tensor[i, 8, 1] = -sun_h[1]
        helio_tensor[i, 8, 2] = sun_h[2]
        helio_tensor[i, 8, 3] = sun_h[3]
        helio_tensor[i, 8, 4] = (helio_tensor[i, 8, 0] - lahiri_ayanamsha_arr[i]) % 360.0

        # ── Upagrahas ────────────────────────────
        try:
            ug = _derive_upagrahas(jd_f, WST_LAT, WST_LON)
            for k, name in enumerate(upagraha_names):
                upagraha_matrix[i, k] = ug[name]
        except Exception as e:
            fail_count += 1
            
    if fail_count > 0:
        print(f"WARNING: Upagraha derivation failed on {fail_count} days")

    # ── Post-loop: Acceleration ─────────────────
    print("Computing acceleration arrays...")
    # Topo (TRAP 3.2.N3 FIX)
    for j in range(12): 
        accel_col = np.empty(N, dtype=np.float64)
        accel_col[0] = 0.0
        accel_col[1:] = np.diff(topo_tensor[:, j, 3])
        topo_tensor[:, j, 7] = accel_col
        
    topo_tensor[:, 12, 7] = topo_tensor[:, 10, 7] # Ketu_True
    topo_tensor[:, 13, 7] = topo_tensor[:, 11, 7] # Ketu_Mean
    topo_tensor[:, 14, 7] = 0.0 # Asc
    topo_tensor[:, 15, 7] = 0.0 # MC

    # Helio (TRAP 3.3.C FIX)
    for j in range(N_HELIO):
        accel_col = np.empty(N, dtype=np.float64)
        accel_col[0] = 0.0
        accel_col[1:] = np.diff(helio_tensor[:, j, 3])
        helio_tensor[:, j, 5] = accel_col

    # ── Assemble Output ──────────────
    print("Assembling output DataFrames...")

    topo_field_map = {0: "Lon_Tropical", 1: "Lat_Ecliptic", 2: "Dist_AU",
                 3: "Speed", 4: "Declination", 5: "RA", 6: "Lon_Sidereal", 7: "Acceleration"}

    col_dict = {}
    for j, name in enumerate(PLANET_NAMES):
        for f, fname in topo_field_map.items():
            col_dict[f"{name}_{fname}"] = topo_tensor[:, j, f]

    col_dict["Lahiri_Ayanamsha"] = lahiri_ayanamsha_arr
    col_dict["KP_Ayanamsha"]     = kp_ayanamsha_arr

    for k, name in enumerate(upagraha_names):
        col_dict[name] = upagraha_matrix[:, k]

    topo_df = pd.DataFrame(col_dict)
    
    # ── Helio Output (TRAP 3.3.H & 3.3.A FIX) ────────
    helio_field_map = {0: "Helio_Lon", 1: "Helio_Lat", 2: "Helio_Dist", 3: "Helio_Speed", 4: "Helio_Lon_Sidereal", 5: "Helio_Acceleration"}
    helio_col_dict = {}
    for j, name in enumerate(HELIO_NAMES):
        for f, fname in helio_field_map.items():
            helio_col_dict[f"{name}_{fname}"] = helio_tensor[:, j, f]
        helio_col_dict[f"{name}_Helio_Is_Retrograde"] = 0 # TRAP 3.3.A

    helio_df = pd.DataFrame(helio_col_dict)

    topo_parquet  = os.path.join(OUTPUT_DIR, "spy_topo_tensor.parquet")
    helio_parquet = os.path.join(OUTPUT_DIR, "spy_helio_tensor.parquet")

    pq.write_table(pa.Table.from_pandas(topo_df), topo_parquet, compression="snappy")
    pq.write_table(pa.Table.from_pandas(helio_df), helio_parquet, compression="snappy")
    
    np.save(os.path.join(OUTPUT_DIR, "spy_topo_tensor_raw.npy"), topo_tensor)
    np.save(os.path.join(OUTPUT_DIR, "spy_helio_tensor_raw.npy"), helio_tensor)

    print(f"\nTopocentric Tensor: {topo_df.shape} -> {topo_parquet}")
    print(f"Heliocentric Tensor: {helio_df.shape} -> {helio_parquet}")
    print("STEP 3.2 & 3.3 COMPLETE.")


if __name__ == "__main__":
    execute_step_3_2()


# CRITICAL BUG FIX #17: Ensure swisseph is closed
import atexit
atexit.register(swe.close)
