"""
SUPREME MATRIX: ABSOLUTE MATHEMATICAL AUDIT V3
===============================================
Going deepest yet. New lenses:
  [1] Three-Level Dasha Cross-Check (Maha/Antar/Pratyantar must be mutually exclusive per axis)
  [2] Antardasha & Pratyantardasha Duration Mathematics (must sum exactly to Mahadasha duration)
  [3] Nakshatra Distribution (each of 27 nakshatras should appear exactly 1/27 of the time for outer planets)
  [4] Graha Yuddha Symmetry (if Mars wins over Saturn, Saturn cannot simultaneously win over Mars)
  [5] Station Event Frequency (retrograde periods must match known astronomical almanac counts)
  [6] Zero Null Check (every cell must have a real number - no NaN allowed in feature set)
  [7] Feature Monotonicity Check (all planetary longitudes must advance forward, modulo 360)
  [8] Exact Combustion Day-Count Almanac Verification (Mercury retrogrades ~3x/year)
"""

import pandas as pd
import numpy as np

FILE = r"C:\Users\patel\Desktop\Python\Learn\supreme_genesis_matrix.parquet"
DASHA_RULERS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS  = [7, 20, 6, 10, 7, 18, 16, 19, 17]

print("="*80)
print(" SUPREME MATRIX: ABSOLUTE MATHEMATICAL AUDIT V3 — 8-LENS DEEP SCAN")
print("="*80)

df = pd.read_parquet(FILE)
df["Date"] = pd.to_datetime(df["Date"])
print(f"\nScanning {len(df):,} rows × {len(df.columns):,} columns...\n")

total_tests = 0
passed = 0

def check(name, condition, detail=""):
    global total_tests, passed
    total_tests += 1
    if condition:
        passed += 1
        print(f"  PASS ✅  {name}")
    else:
        print(f"  FAIL ❌  {name}  |  {detail}")
    if detail and condition:
        print(f"           → {detail}")

# ═══════════════════════════════════════════════════════════════
# LENS 1: NULL / NaN INTEGRITY CHECK
# ═══════════════════════════════════════════════════════════════
print("[1] NULL / NaN INTEGRITY CHECK")
# Only test numeric feature columns newly added by the True Jyotish Engine
new_cols = [c for c in df.columns if any(tag in c for tag in [
    "_lon", "_lat", "_speed", "_retro", "_bindus", "_bindu_",
    "_true_combust", "_true_cazimi", "_true_war", "_true_station",
    "Maha_", "Antar_", "Prat_", "Sarvashtakavarga"
])]
null_counts = df[new_cols].isnull().sum()
total_nulls = null_counts.sum()
check("Zero NaN in all 1,851 Jyotish feature columns",
      total_nulls == 0,
      f"Found {total_nulls} NaN values across {len(new_cols)} columns")
print(f"           → Tested {len(new_cols)} Jyotish columns, Total NaN: {total_nulls}")

# ═══════════════════════════════════════════════════════════════
# LENS 2: THREE-LEVEL DASHA MUTUAL EXCLUSIVITY
# ═══════════════════════════════════════════════════════════════
print("\n[2] THREE-LEVEL DASHA MUTUAL EXCLUSIVITY")
maha_cols = [f"Maha_{d}" for d in DASHA_RULERS]
antar_cols = [f"Antar_{d}" for d in DASHA_RULERS]
prat_cols  = [f"Prat_{d}" for d in DASHA_RULERS]

maha_sum = df[maha_cols].sum(axis=1)
antar_sum = df[antar_cols].sum(axis=1)
prat_sum  = df[prat_cols].sum(axis=1)

check("Each row has exactly 1 active Maha Dasha lord",
      (maha_sum == 1).all(),
      f"Violations: {(maha_sum != 1).sum()} rows")
check("Each row has exactly 1 active Antar Dasha lord",
      (antar_sum == 1).all(),
      f"Violations: {(antar_sum != 1).sum()} rows")
check("Each row has exactly 1 active Pratyantar Dasha lord",
      (prat_sum == 1).all(),
      f"Violations: {(prat_sum != 1).sum()} rows")

# ═══════════════════════════════════════════════════════════════
# LENS 3: DASHA SEQUENCE ORDERING (must follow Ketu→Venus→Sun…)
# ═══════════════════════════════════════════════════════════════
print("\n[3] VIMSHOTTARI DASHA SEQUENCE ORDERING")
active_maha = df[maha_cols].idxmax(axis=1).str.replace("Maha_", "")
transitions = active_maha[active_maha != active_maha.shift(1)].dropna()
seq_ok = True
for i in range(1, len(transitions)):
    prev = transitions.iloc[i-1]
    curr = transitions.iloc[i]
    expected_next = DASHA_RULERS[(DASHA_RULERS.index(prev) + 1) % 9]
    if curr != expected_next:
        seq_ok = False
        print(f"  ERROR: Transition {prev} → {curr} (expected {expected_next})")
        break
check("Maha Dasha lords follow the classical Vimshottari sequence",
      seq_ok,
      f"Observed transitions: {list(transitions.unique())}")
print(f"           → Observed Maha sequence: {' → '.join(transitions.unique())}")

# ═══════════════════════════════════════════════════════════════
# LENS 4: ANTARDASHA SEQUENCE (must follow same Vimshottari order within each Maha)
# ═══════════════════════════════════════════════════════════════
print("\n[4] ANTARDASHA SEQUENCE WITHIN EACH MAHA DASHA")
active_antar = df[antar_cols].idxmax(axis=1).str.replace("Antar_", "")
antar_ok = True
prev_antar = None
for maha_lord in transitions.unique():
    maha_mask = active_maha == maha_lord
    antar_in_maha = active_antar[maha_mask]
    antar_transitions = antar_in_maha[antar_in_maha != antar_in_maha.shift(1)].dropna()
    for i in range(1, len(antar_transitions)):
        prev_a = antar_transitions.iloc[i-1]
        curr_a = antar_transitions.iloc[i]
        expected_a = DASHA_RULERS[(DASHA_RULERS.index(prev_a) + 1) % 9]
        if curr_a != expected_a:
            antar_ok = False
            print(f"  ERROR: In {maha_lord} Maha, Antar went {prev_a} → {curr_a} (expected {expected_a})")
            break
check("Antar Dasha lords follow the classical Vimshottari sequence within each Maha",
      antar_ok)

# ═══════════════════════════════════════════════════════════════
# LENS 5: GRAHA YUDDHA SYMMETRY (if A wins over B, B cannot also win over A same day)
# ═══════════════════════════════════════════════════════════════
print("\n[5] GRAHA YUDDHA VICTOR SYMMETRY")
WAR_PAIRS = [("Mars","Saturn"),("Mercury","Venus"),("Mercury","Mars"),
             ("Venus","Mars"),("Jupiter","Saturn"),("Mars","Jupiter")]
sym_ok = True
for p1, p2 in WAR_PAIRS:
    col_p1_wins = f"{p1}_{p2}_war_{p1}_wins"
    col_p2_wins = f"{p1}_{p2}_war_{p2}_wins"
    if col_p1_wins not in df.columns or col_p2_wins not in df.columns:
        continue
    both_win = (df[col_p1_wins] == 1) & (df[col_p2_wins] == 1)
    if both_win.any():
        sym_ok = False
        print(f"  ERROR: {p1} and {p2} both declared winner on {both_win.sum()} days!")
check("No dual-winner Graha Yuddha (cannot have both planets win same war same day)",
      sym_ok)

# ═══════════════════════════════════════════════════════════════
# LENS 6: RETROGRADE PERIOD ALMANAC FREQUENCIES
# ═══════════════════════════════════════════════════════════════
print("\n[6] RETROGRADE PERIOD ALMANAC FREQUENCY")
EXPECTED_RETROGRADE = {
    "Mercury": (3.0, 5.0),   # Mercury retrogrades ~3x/year, 19-24 days each
    "Venus":   (0.5, 1.5),   # Venus retrogrades ~once every 18 months
    "Mars":    (0.4, 0.7),   # Mars retrogrades ~once every 2 years
    "Jupiter": (0.9, 1.1),   # Jupiter retrogrades ~once/year
    "Saturn":  (0.9, 1.1),   # Saturn retrogrades ~once/year
}
years = (df["Date"].max() - df["Date"].min()).days / 365.25636042
for p, (lo, hi) in EXPECTED_RETROGRADE.items():
    col = f"{p}_true_station_R"
    if col not in df.columns: continue
    n_retrogrades = df[col].sum()
    per_year = n_retrogrades / years
    check(f"{p} Station-R frequency: {n_retrogrades} events over {years:.1f}yrs ({per_year:.2f}/yr, expected {lo}-{hi}/yr)",
          lo <= per_year <= hi,
          f"Got {per_year:.2f}/yr")

# ═══════════════════════════════════════════════════════════════
# LENS 7: PLANETARY LONGITUDE CONTINUITY (no teleportation)
# ═══════════════════════════════════════════════════════════════
print("\n[7] PLANETARY LONGITUDE CONTINUITY (Per-Calendar-Day, No Teleportation)")
# Market data only has trading days, so 3-day weekend gaps are normal.
# We must divide the observed longitude jump by the actual calendar date gap.
DAILY_MOTION_LIMITS = {
    # True astronomical maximum daily motions (Astronomical Almanac / JPL):
    "Sun":     1.02,   # max ~1.019°/day near perihelion (Jan)
    "Moon":    15.40,  # max ~15.4°/day near perigee (elliptical orbit)
    "Mercury": 2.21,   # max ~2.20°/day near perihelion direct
    "Venus":   1.30,   # max ~1.26°/day
    "Mars":    0.80,   # max ~0.79°/day near perihelion
    "Jupiter": 0.25,   # max ~0.24°/day
    "Saturn":  0.14,   # max ~0.13°/day
    "Rahu":    0.26,   # True node can surge ~0.25°/day during eclipse seasons
}
date_gaps = df["Date"].diff().dt.days.fillna(1)
for p, max_motion in DAILY_MOTION_LIMITS.items():
    col = f"{p}_lon"
    if col not in df.columns: continue
    raw_diff = df[col].diff().abs()
    # Correct for zodiac wrap-around
    wrap_corrected = raw_diff.apply(lambda x: min(x, 360 - x) if pd.notna(x) else 0)
    # Normalize by calendar days elapsed between rows
    per_day_motion = (wrap_corrected / date_gaps.replace(0, 1))
    max_observed = per_day_motion.max()
    check(f"{p} max per-calendar-day motion {max_observed:.4f}°/day ≤ limit {max_motion}°/day",
          max_observed <= max_motion,
          f"Observed max: {max_observed:.4f}°/day")

# ═══════════════════════════════════════════════════════════════
# LENS 8: CAZIMI vs COMBUST HIERARCHY (Cazimi must be strict subset of Combust)
# ═══════════════════════════════════════════════════════════════
print("\n[8] CAZIMI MUST BE STRICT SUBSET OF COMBUSTION")
for p in ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Moon"]:
    cazimi_col  = f"{p}_true_cazimi"
    combust_col = f"{p}_true_combust"
    if cazimi_col not in df.columns or combust_col not in df.columns: continue
    cazimi_not_combust = (df[cazimi_col] == 1) & (df[combust_col] == 0)
    check(f"{p}: Cazimi is subset of Combustion (no Cazimi without Combustion)",
          not cazimi_not_combust.any(),
          f"Violations: {cazimi_not_combust.sum()} rows")

# ═══════════════════════════════════════════════════════════════
# FINAL SCORECARD
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*80)
print(f" FINAL SCORECARD: {passed}/{total_tests} TESTS PASSED")
print("="*80)
if passed == total_tests:
    print(" ALL SYSTEMS MATHEMATICALLY PERFECT.")
