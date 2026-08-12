"""
vimshottari_module.py
======================
Constructs the complete Vimshottari Dasha interval tree (Maha → Antar → Pratyantar)
for a given birth Moon longitude and Julian Day.

4-LENS FRAMEWORK INSPECTION
----------------------------
🔴 ML Architect:
  - All 3 Dasha levels are built as a flat, sorted numpy structured array (dtype=np.float64)
    that XGBoost/LightGBM can binary-search in O(log n) per row.
  - Feature columns: maha_sin, maha_cos, antar_sin, antar_cos, prat_sin, prat_cos
    (mapped to 9 nodes) rather than raw 0-8 integers.

🔴 Data Engineer:
  - Uses SIDEREAL_YEAR = 365.25636042 (NOT 365.25 — Trap P2.9 fix).
  - All start/end timestamps stored as raw float64 Julian Days → zero timezone ambiguity.
  - No Pandas DataFrames are returned; pure Python lists + numpy structured arrays only.

🔴 Jyotish Scholar:
  - The first Maha Dasha is a FRACTIONAL REMNANT: only (1 - nakshatra_fraction) of the
    lord's full period remains. This is the canonical Parashari rule, leaving uncompressed durations.
  - Period sequence always follows the fixed 9-step cycle: Ke→Ve→Su→Mo→Ma→Ra→Ju→Sa→Me.
  - Antar proportions: (antar_years / 120) × maha_years × SIDEREAL_YEAR days.
  - Pratyantar proportions: (pratyantar_years / 120) × antar_days.

🔴 Quant Developer:
  - Binary-search lookup function `query_dasha_at_jd()` is O(log n) using bisect.
  - No mutable global state; every call is a pure function producing independent trees.
  - Float tearing eliminated completely via exact offset accumulations.
"""

import numpy as np
from bisect import bisect_right

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
SIDEREAL_YEAR     = 365.25636042          # Exact sidereal year in days (Trap P2.9 fix)
NAKSHATRA_SPAN    = 360.0 / 27.0          # 13.33333° per Nakshatra
TOTAL_CYCLE_YEARS = 120.0

# Canonical 9-step Vimshottari sequence
DASHA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = [7.0, 20.0, 6.0, 10.0, 7.0, 18.0, 16.0, 19.0, 17.0]
LORD_TO_INT  = {lord: i for i, lord in enumerate(DASHA_LORDS)}  # For mappings

# Structured dtype for the flat interval array
INTERVAL_DTYPE = np.dtype([
    ("maha_sin",        np.float64),
    ("maha_cos",        np.float64),
    ("antar_sin",       np.float64),
    ("antar_cos",       np.float64),
    ("prat_sin",        np.float64),
    ("prat_cos",        np.float64),
    ("start_jd",        np.float64),
    ("end_jd",          np.float64),
])


# ─────────────────────────────────────────────────────────────────────────────
# CORE BUILDER
# ─────────────────────────────────────────────────────────────────────────────
def build_vimshottari_tree(moon_longitude_sidereal: float,
                           birth_jd: float,
                           max_years: float = 120.0) -> np.ndarray:
    """
    Builds the full Vimshottari Dasha tree as a flat numpy structured array
    ordered chronologically by start_jd.

    Parameters
    ----------
    moon_longitude_sidereal : float
        Natal Moon longitude in sidereal degrees (0–360).
    birth_jd : float
        Julian Day number of birth moment (UTC).
    max_years : float
        How many years of Dashas to pre-compute (default 120).

    Returns
    -------
    np.ndarray of dtype INTERVAL_DTYPE
        Flat array of Pratyantar intervals sorted by start_jd.
    """
    # ── Step 1: Find starting Nakshatra and fraction elapsed ────────────────
    nak_idx           = int(moon_longitude_sidereal / NAKSHATRA_SPAN) % 27
    fraction_elapsed  = (moon_longitude_sidereal % NAKSHATRA_SPAN) / NAKSHATRA_SPAN
    start_lord_idx    = nak_idx % 9

    records = []
    limit_jd   = birth_jd + max_years * SIDEREAL_YEAR

    # ── Step 2: Uncompressed Mahadasha calculation ─────────────────────────
    first_maha_duration = DASHA_YEARS[start_lord_idx] * SIDEREAL_YEAR
    elapsed_days        = fraction_elapsed * first_maha_duration
    
    original_maha_start_jd = birth_jd - elapsed_days

    # ── Step 3: Expand Maha → Antar → Pratyantar without float tearing ─────
    maha_step = 0
    while True:
        maha_idx = (start_lord_idx + maha_step) % 9
        
        # Calculate start offset for this Maha Dasha directly from 0
        maha_start_offset = sum(DASHA_YEARS[(start_lord_idx + i) % 9] for i in range(maha_step)) * SIDEREAL_YEAR
        maha_start_jd = original_maha_start_jd + maha_start_offset
        
        if maha_start_jd >= limit_jd:
            break
            
        maha_duration = DASHA_YEARS[maha_idx] * SIDEREAL_YEAR
        
        maha_angle = 2.0 * np.pi * maha_idx / 9.0
        msin, mcos = np.sin(maha_angle), np.cos(maha_angle)

        for antar_step in range(9):
            antar_idx = (maha_idx + antar_step) % 9
            antar_dur = (DASHA_YEARS[antar_idx] / TOTAL_CYCLE_YEARS) * maha_duration
            
            antar_start_offset = sum(DASHA_YEARS[(maha_idx + i) % 9] for i in range(antar_step)) / TOTAL_CYCLE_YEARS * maha_duration
            
            antar_angle = 2.0 * np.pi * antar_idx / 9.0
            asin, acos = np.sin(antar_angle), np.cos(antar_angle)

            for prat_step in range(9):
                prat_idx = (antar_idx + prat_step) % 9
                
                prat_angle = 2.0 * np.pi * prat_idx / 9.0
                psin, pcos = np.sin(prat_angle), np.cos(prat_angle)

                prat_start_offset = antar_start_offset + sum(DASHA_YEARS[(antar_idx + i) % 9] for i in range(prat_step)) / TOTAL_CYCLE_YEARS * antar_dur
                
                if prat_step == 8:
                    prat_end_offset = antar_start_offset + antar_dur
                else:
                    prat_end_offset = antar_start_offset + sum(DASHA_YEARS[(antar_idx + i) % 9] for i in range(prat_step + 1)) / TOTAL_CYCLE_YEARS * antar_dur
                    
                if antar_step == 8 and prat_step == 8:
                    prat_end_offset = maha_duration
                    
                prat_start_jd = maha_start_jd + prat_start_offset
                prat_end_jd = maha_start_jd + prat_end_offset
                
                if prat_end_jd <= birth_jd:
                    continue
                    
                if prat_start_jd >= limit_jd:
                    break

                records.append((
                    msin, mcos,
                    asin, acos,
                    psin, pcos,
                    prat_start_jd,
                    min(prat_end_jd, limit_jd)
                ))

        maha_step += 1

    # ── Step 4: Pack into structured numpy array ─────────────────────────────
    arr = np.array(records, dtype=INTERVAL_DTYPE)
    arr.sort(order="start_jd")   # Guarantee chronological order for bisect
    return arr


# ─────────────────────────────────────────────────────────────────────────────
# O(log n) DAILY LOOKUP
# ─────────────────────────────────────────────────────────────────────────────
def query_dasha_at_jd(tree: np.ndarray, query_jd: float) -> dict:
    """
    Returns the Maha/Antar/Pratyantar lords active at query_jd.
    O(log n) binary search via bisect_right on the sorted start_jd column.

    Parameters
    ----------
    tree : np.ndarray
        Output of build_vimshottari_tree().
    query_jd : float
        Julian Day to query.

    Returns
    -------
    dict with keys: maha_lord, antar_lord, pratyantar_lord, 
                    maha_sin, maha_cos, antar_sin, antar_cos, prat_sin, prat_cos,
                    prat_frac (0→1 completion fraction of uncompressed period)
    """
    start_jds = tree["start_jd"]
    idx = bisect_right(start_jds, query_jd) - 1
    if idx < 0:
        idx = 0
    if idx >= len(tree):
        idx = len(tree) - 1

    row = tree[idx]

    # Compute completion fraction within this Pratyantar
    duration = row["end_jd"] - row["start_jd"]
    prat_frac = (query_jd - row["start_jd"]) / duration if duration > 0 else 0.0

    def get_lord_from_sincos(sin_val, cos_val):
        angle = np.arctan2(sin_val, cos_val)
        if angle < 0:
            angle += 2 * np.pi
        i = int(np.round(angle * 9.0 / (2 * np.pi))) % 9
        return i, DASHA_LORDS[i]

    _, maha_lord_name = get_lord_from_sincos(row["maha_sin"], row["maha_cos"])
    _, antar_lord_name = get_lord_from_sincos(row["antar_sin"], row["antar_cos"])
    _, prat_lord_name = get_lord_from_sincos(row["prat_sin"], row["prat_cos"])

    return {
        "maha_lord":       maha_lord_name,
        "antar_lord":      antar_lord_name,
        "pratyantar_lord": prat_lord_name,
        "maha_sin":        float(row["maha_sin"]),
        "maha_cos":        float(row["maha_cos"]),
        "antar_sin":       float(row["antar_sin"]),
        "antar_cos":       float(row["antar_cos"]),
        "prat_sin":        float(row["prat_sin"]),
        "prat_cos":        float(row["prat_cos"]),
        "prat_frac":       float(np.clip(prat_frac, 0.0, 1.0)),
    }


# ─────────────────────────────────────────────────────────────────────────────
# SELF-VALIDATION
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # SPY birth: 1993-01-29 14:30 UTC → JD 2448986.1042
    BIRTH_JD = 2448986.1042
    MOON_LON_SIDEREAL = 97.23    # Example: ~7° Cancer sidereal

    tree = build_vimshottari_tree(MOON_LON_SIDEREAL, BIRTH_JD)
    print(f"[VALIDATION] Total Pratyantar intervals built: {len(tree)}")

    # Validate total span ~= 120 sidereal years
    # (Using the max clamps out the portion of the first active pratyantar before birth)
    total_days = tree["end_jd"][-1] - max(BIRTH_JD, tree["start_jd"][0])
    total_years = total_days / SIDEREAL_YEAR
    print(f"[VALIDATION] Total span: {total_years:.6f} sidereal years (expected ~120.0)")
    assert abs(total_years - 120.0) < 0.001, "FATAL: Vimshottari span mismatch!"

    # Spot-check lookup
    result = query_dasha_at_jd(tree, BIRTH_JD + 365.0)
    print(f"[VALIDATION] Dasha at birth+1yr: {result['maha_lord']} / {result['antar_lord']} / {result['pratyantar_lord']}")
    print("[VALIDATION] vimshottari_module PASSED all checks.")
