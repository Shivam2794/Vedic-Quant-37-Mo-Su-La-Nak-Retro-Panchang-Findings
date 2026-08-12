"""
VEDIC ALPHA JYOTISH AUGMENTER v2
==================================
The matrix already has: Shadbala (464 cols), Dignity/Exaltation (552 cols),
Aspects (320 cols), Panchang (88 cols), Pushkar (160 cols), Nakshatra (16 cols).

What's MISSING (adding now):
  1. Combustion / Cazimi           — planet proximity to Sun
  2. Retrograde flags + Station days — reversal moments
  3. Avasthas                      — planetary age state (0-4)
  4. Graha Yuddha                  — planetary war (within 1 degree)
  5. Nakshatra Pada                — 108-subdivision Moon resolution
  6. Vimshottari Dasha (NYSE)      — macro period ruler
  7. Ashtakvarga Bindus (NYSE)     — transit strength per sign

Problem: The matrix has no raw longitude columns (T_ prefix features are
pre-encoded). We derive positions from the existing Dignity columns.
"""

import os, numpy as np, pandas as pd, warnings
from datetime import date
warnings.filterwarnings("ignore")

BASE_DIR    = r"C:\Users\patel\Desktop\Python\Learn"
MATRIX_FILE = os.path.join(BASE_DIR, "genesis_9000_MUNDANE.parquet")
OUTPUT_FILE = os.path.join(BASE_DIR, "vedic_jyotish_features.parquet")

print("Loading matrix...")
df = pd.read_parquet(MATRIX_FILE)
df["Date"] = pd.to_datetime(df["Date"])
print(f"Loaded: {len(df):,} rows x {len(df.columns)} cols")
print(f"Range : {df['Date'].min().date()} → {df['Date'].max().date()}")

# Planet abbreviations as used in column names
PLANET_ABBR = {
    "Sun": "Sun", "Moon": "Moo", "Mercury": "Mer",
    "Venus": "Ven", "Mars": "Mar", "Jupiter": "Jup",
    "Saturn": "Sat", "Rahu": "Rah", "Ketu": "Ket"
}
PLANETS = list(PLANET_ABBR.keys())

feats = pd.DataFrame({"Date": df["Date"]}, index=df.index)

# ═══════════════════════════════════════════════════════════════════════
# COMBUSTION — derive from Dignity_Score + Exalted/Debilitated cols
# We don't have raw Sun-to-planet degrees, so we proxy combustion via
# the sign-based features: if a planet is in the same sign as the Sun
# (T_Sun_OwnSign would be Sun-ruled), we detect adjacency.
#
# Better approach: Infer planet sign from the Dignity columns.
# Each planet has: T_X_Exalted (binary), T_X_OwnSign (binary), T_X_Dignity_Score (numeric)
# The Dignity_Score encodes: exalted=highest, own=high, neutral=0, debil=lowest
# But this doesn't give us degrees.
#
# TRUE FIX: We need to reconstruct planet positions from Panchang.
# The Moon_Nak_Idx (0-26) gives Moon position in 13.33° bins.
# For other planets, we use sign columns to derive 30° bins.
# ═══════════════════════════════════════════════════════════════════════

# Detect sign columns: T_DoubleTr_Sign0..11 appear to be sign-count columns
# Let's check what sign information is available
sign_cols = [c for c in df.columns if "Sign" in c and "Own" not in c]
print(f"\nSign-related cols: {sign_cols[:10]}")

# The Dignity_Score is continuous. Exalted=1 tells us which sign.
# We can reconstruct approximate longitude from these binary flags.
EXALT_SIGN_DEG = {
    "Sun": 10,    # Aries
    "Moo": 33,    # Taurus
    "Mar": 298,   # Capricorn
    "Mer": 165,   # Virgo
    "Jup": 95,    # Cancer
    "Ven": 357,   # Pisces
    "Sat": 200,   # Libra
    "Rah": 63,    # Taurus (approx)
    "Ket": 243,   # Scorpio (approx)
}
DEBIL_SIGN_DEG = {k: (v + 180) % 360 for k, v in EXALT_SIGN_DEG.items()}

# ═══════════════════════════════════════════════════════════════════════
# FEATURE 1: AVASTHAS from Dignity_Score
# Dignity_Score is a proxy for planetary strength.
# Map to Avastha-like bins: Strong=Yuva, Weak=Mrita, etc.
# ═══════════════════════════════════════════════════════════════════════
print("\n[1/6] Avastha proxies from Dignity_Score...")
n_av = 0
for planet, abbr in PLANET_ABBR.items():
    dig_col = f"T_{abbr}_Dignity_Score"
    if dig_col not in df.columns: continue
    score = df[dig_col]
    # Exalted → Yuva (peak), OwnSign → Kumara, Neutral → Yuva,
    # Debilitated → Mrita
    exalt_col = f"T_{abbr}_Exalted"
    debil_col = f"T_{abbr}_Debilitated"
    own_col   = f"T_{abbr}_OwnSign"
    if all(c in df.columns for c in [exalt_col, debil_col, own_col]):
        feats[f"{abbr}_avastha_yuva"]  = df[exalt_col].astype(np.int8)
        feats[f"{abbr}_avastha_mrita"] = df[debil_col].astype(np.int8)
        feats[f"{abbr}_avastha_own"]   = df[own_col].astype(np.int8)
        n_av += 3
print(f"  Added {n_av} avastha-proxy features")

# ═══════════════════════════════════════════════════════════════════════
# FEATURE 2: COMBUSTION PROXIES
# Since we lack raw degrees, use Shadbala_Chesta as a proxy.
# Chesta Bala = motional strength. A combust planet has near-zero Chesta Bala
# because it moves with the Sun and loses independent motion energy.
# ═══════════════════════════════════════════════════════════════════════
print("\n[2/6] Combustion proxies from Shadbala_Chesta...")
n_comb = 0
for planet, abbr in PLANET_ABBR.items():
    chesta_col = f"T_{abbr}_Shadbala_Chesta"
    if chesta_col not in df.columns: continue
    chesta = df[chesta_col]
    # Low Chesta = likely combust (no independent motion)
    # Normalize: flag bottom 10th percentile as "combust proxy"
    threshold = chesta.quantile(0.10)
    feats[f"{abbr}_combust_proxy"] = (chesta < threshold).astype(np.int8)
    feats[f"{abbr}_chesta_bala"]   = chesta.values
    n_comb += 2
print(f"  Added {n_comb} combustion-proxy features")

# ═══════════════════════════════════════════════════════════════════════
# FEATURE 3: RETROGRADE + STATION from Shadbala_Chesta changes
# Retrograde = planet moving backward → Chesta Bala changes sign/sign convention
# The actual retrograde flag should be derivable from Chesta Bala sign.
# In Shadbala: retrograde planets get HIGHER Chesta Bala (they're "working harder")
# Station = Chesta near zero (momentary standstill)
# ═══════════════════════════════════════════════════════════════════════
print("\n[3/6] Retrograde & Station from Chesta Bala changes...")
n_retro = 0
df_s = df.sort_values("Date").copy()
for planet, abbr in PLANET_ABBR.items():
    if planet in ["Sun", "Moon"]: continue  # don't go retrograde
    chesta_col = f"T_{abbr}_Shadbala_Chesta"
    if chesta_col not in df_s.columns: continue
    chesta = df_s[chesta_col].copy()
    chesta_diff = chesta.diff()
    # Station proxy: chesta value is near zero (momentary halt before reversal)
    station_threshold = chesta.abs().quantile(0.05)
    feats.loc[df_s.index, f"{abbr}_station_proxy"] = (chesta.abs() < station_threshold).astype(np.int8).values
    # Chesta_diff sign change = direction reversal
    feats.loc[df_s.index, f"{abbr}_chesta_reversal"] = (
        (chesta_diff > 0) != (chesta_diff.shift(1) > 0)
    ).astype(np.int8).values
    n_retro += 2
print(f"  Added {n_retro} retrograde/station proxy features")

# ═══════════════════════════════════════════════════════════════════════
# FEATURE 4: GRAHA YUDDHA (Planetary War) from Aspect columns
# T_X_Mutual_Aspect_Count = how many mutual aspects planet X has
# Two planets in war (within 1°) would show conjunct aspect.
# Proxy: both planets in same sign (Dignity_Score both near 0)
# AND both OwnSign=0, Exalted=0, Debilitated=0 → neutral sign (likely same)
# Better: use the DoubleTr sign columns to detect co-occupation.
# ═══════════════════════════════════════════════════════════════════════
print("\n[4/6] Graha Yuddha proxies from Aspect & Sign features...")
# T_DoubleTr_Sign0..11 = number of planets transiting each sign (0=Aries..11=Pisces)
double_tr_cols = [c for c in df.columns if c.startswith("T_DoubleTr_Sign") and
                  not any(k in c for k in ["lag","diff","Active"])]
n_war = 0
if double_tr_cols:
    for sig_col in double_tr_cols:
        sign_num = sig_col.replace("T_DoubleTr_Sign","")
        if sign_num.isdigit():
            feats[f"sign{sign_num}_crowded"] = (df[sig_col] >= 2).astype(np.int8)
            feats[f"sign{sign_num}_triple"]  = (df[sig_col] >= 3).astype(np.int8)
            n_war += 2
    # Also use the active count
    if "T_DoubleTr_Active_Count" in df.columns:
        feats["double_transit_active"] = df["T_DoubleTr_Active_Count"].values
        n_war += 1
print(f"  Added {n_war} Graha Yuddha proxy features (sign co-occupation)")

# ═══════════════════════════════════════════════════════════════════════
# FEATURE 5: NAKSHATRA PADA from Moon_Nak_Idx
# Moon_Nak_Idx is 0-26 (nakshatra number). We need more granularity.
# The Moon moves ~13.2° per day. Within a nakshatra (13.33°), we can
# estimate the pada from the fractional position change.
# ═══════════════════════════════════════════════════════════════════════
print("\n[5/6] Nakshatra Pada features...")
n_pada = 0
if "Moon_Nak_Idx" in df.columns:
    moon_nak = df["Moon_Nak_Idx"]
    feats["moon_nak_idx"]       = moon_nak.values.astype(np.int8)
    # Lag differences give pada-level resolution
    feats["moon_nak_entered"]   = (moon_nak != moon_nak.shift(1)).astype(np.int8)  # nakshatra ingress
    # Pushkar nakshatras (highly auspicious)
    PUSHKARA_NAKS = {0,3,5,10,16,20,23,26}  # Ashwini,Rohini,Ardra,Purva Phalguni,Anuradha,Uttarashada,Shatabhisha,Revati
    feats["moon_pushkara_nak"]  = moon_nak.isin(PUSHKARA_NAKS).astype(np.int8)
    # Gandanta nakshatras (fire-water junction = volatile)
    GANDANTA_NAKS = {8, 9, 17, 18, 26, 0}   # last of fire + first of water signs
    feats["moon_gandanta_nak"]  = moon_nak.isin(GANDANTA_NAKS).astype(np.int8)
    # Moon nakshatra speed (changes per day = indication of pada)
    nak_speed = moon_nak.diff().abs()
    feats["moon_nak_speed"]     = nak_speed.values
    n_pada = 5
print(f"  Added {n_pada} nakshatra-pada features")

# ═══════════════════════════════════════════════════════════════════════
# FEATURE 6: VIMSHOTTARI DASHA (NYSE Natal Chart)
# ═══════════════════════════════════════════════════════════════════════
print("\n[6/6] Vimshottari Dasha (NYSE natal: May 17, 1792)...")

DASHA_ORDER   = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
DASHA_PERIODS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
PLANET_IDX    = {p: i for i, p in enumerate(DASHA_ORDER)}
NYSE_NATAL    = date(1792, 5, 17)
FIRST_REMAIN  = 4.9  # years remaining in Ketu dasha at birth

def compute_dasha(target_date):
    if hasattr(target_date, 'date'): target_date = target_date.date()
    elif isinstance(target_date, str): target_date = date.fromisoformat(str(target_date)[:10])
    total_yrs = (target_date - NYSE_NATAL).days / 365.25636042
    elapsed = 0.0; idx = 0; first = True
    while True:
        period = FIRST_REMAIN if first else DASHA_PERIODS[DASHA_ORDER[idx]]
        if elapsed + period > total_yrs: break
        elapsed += period; idx = (idx + 1) % 9; first = False
    maha_lord  = DASHA_ORDER[idx]
    maha_years = FIRST_REMAIN if first else DASHA_PERIODS[maha_lord]
    maha_frac  = (total_yrs - elapsed) / maha_years
    # Antardasha
    antar_idx = idx; antar_acc = 0.0; maha_yrs_elapsed = maha_frac * maha_years
    for _ in range(9):
        ay = maha_years * DASHA_PERIODS[DASHA_ORDER[antar_idx]] / 120.0
        if antar_acc + ay > maha_yrs_elapsed: break
        antar_acc += ay; antar_idx = (antar_idx + 1) % 9
    antar_lord  = DASHA_ORDER[antar_idx]
    antar_years = maha_years * DASHA_PERIODS[DASHA_ORDER[antar_idx]] / 120.0
    antar_frac  = (maha_yrs_elapsed - antar_acc) / antar_years if antar_years > 0 else 0
    # Pratyantar
    prat_idx = antar_idx; prat_acc = 0.0; antar_yrs_elapsed = antar_frac * antar_years
    for _ in range(9):
        py = antar_years * DASHA_PERIODS[DASHA_ORDER[prat_idx]] / 120.0
        if prat_acc + py > antar_yrs_elapsed: break
        prat_acc += py; prat_idx = (prat_idx + 1) % 9
    return {
        "dasha_maha":        PLANET_IDX[maha_lord],
        "dasha_antar":       PLANET_IDX[antar_lord],
        "dasha_prat":        PLANET_IDX[DASHA_ORDER[prat_idx]],
        "dasha_maha_frac":   round(maha_frac, 4),
        "dasha_antar_frac":  round(antar_frac, 4),
        # Binary flags for each planet
        **{f"dasha_{p.lower()}_maha":  int(maha_lord == p)  for p in DASHA_ORDER},
        **{f"dasha_{p.lower()}_antar": int(antar_lord == p) for p in DASHA_ORDER},
        # Interaction: transit planet matches dasha lord
        "dasha_maha_idx":   PLANET_IDX[maha_lord],
        "dasha_antar_idx":  PLANET_IDX[antar_lord],
    }

dasha_records = [compute_dasha(d) for d in df["Date"].dt.date]
dasha_df = pd.DataFrame(dasha_records, index=df.index)
for col in dasha_df.columns:
    feats[col] = dasha_df[col].values
n_dasha = len(dasha_df.columns)
print(f"  Added {n_dasha} Dasha features")

# ─── Interaction: Shadbala_Total × Dasha match ──────────────────────
# If Jupiter is the Maha Dasha lord AND Jupiter has high Shadbala → double signal
PLANET_ABBR_DASHA = {
    "Jupiter":"Jup","Saturn":"Sat","Mars":"Mar","Venus":"Ven",
    "Mercury":"Mer","Moon":"Moo","Sun":"Sun","Rahu":"Rah","Ketu":"Ket"
}
n_inter = 0
for planet in ["Jupiter","Saturn","Mars","Mercury","Venus","Moon"]:
    abbr = PLANET_ABBR_DASHA[planet]
    shad_col  = f"T_{abbr}_Shadbala_Total"
    dasha_col = f"dasha_{planet.lower()}_maha"
    if shad_col in df.columns and dasha_col in feats.columns:
        shad_strong = (df[shad_col] > df[shad_col].median()).astype(int)
        dasha_active = feats[dasha_col].astype(int)
        feats[f"{abbr}_strong_in_{planet.lower()}_dasha"] = (shad_strong * dasha_active).astype(np.int8)
        n_inter += 1
print(f"  Added {n_inter} Shadbala x Dasha interaction features")

# ═══════════════════════════════════════════════════════════════════════
# SAVE & SUMMARY
# ═══════════════════════════════════════════════════════════════════════
n_total = len(feats.columns) - 1
feats.to_parquet(OUTPUT_FILE, index=False)

print(f"\n{'='*70}")
print(f" JYOTISH AUGMENTATION COMPLETE")
print(f"{'='*70}")
print(f" New Jyotish features generated : {n_total}")
print(f" Saved to: {OUTPUT_FILE}")

# What the FULL matrix now contains (existing + new)
print(f"\n COMPLETE VEDIC FEATURE INVENTORY:")
print(f" {'Category':<22} {'Count':>6}  {'Status'}")
print(f" {'-'*50}")
cats = {
    "Panchang (5 elements)":  len([c for c in df.columns if any(k in c for k in ['Tithi','Paksha','Vara','Karana','Yoga','Vishti','Vyatipata','Vaidhriti','Total_Panchang'])]),
    "Nakshatra/Pada":         len([c for c in df.columns if 'Nak' in c]),
    "Dignity/Exalt/Debil":   len([c for c in df.columns if any(k in c for k in ['Dignity','Exalted','Debil','Moola','OwnSign','Vargottama','Gandanta'])]),
    "Shadbala (6 components)":len([c for c in df.columns if 'Shadbala' in c]),
    "Planetary Aspects":      len([c for c in df.columns if 'Aspect' in c or 'Mutual' in c]),
    "Pushkar Navamsha":       len([c for c in df.columns if 'Pushkar' in c]),
    "Double Transit":         len([c for c in df.columns if 'DoubleTr' in c]),
    "NEW: Avastha proxies":   n_av,
    "NEW: Combustion proxy":  n_comb,
    "NEW: Station proxies":   n_retro,
    "NEW: Graha Yuddha proxy":n_war,
    "NEW: Nakshatra detail":  n_pada,
    "NEW: Dasha (NYSE natal)":n_dasha + n_inter,
}
total = 0
for cat, cnt in cats.items():
    tag = "✅ IN MATRIX" if "NEW" not in cat else "🆕 ADDED NOW"
    if cnt == 0: tag = "❌ MISSING"
    print(f" {cat:<28} {cnt:>5}  {tag}")
    total += cnt
print(f" {'─'*50}")
print(f" {'TOTAL FEATURES':<28} {total:>5}")

# Remaining gaps
print(f"\n STILL MISSING (requires natal chart + raw positions):")
gaps = {
    "Ashtakvarga Bindus": "Needs NYSE natal chart bindu table computation",
    "True Combustion (degrees)": "Needs raw Sun-planet angular difference (no longitude in matrix)",
    "True Retrograde flag": "Needs raw daily longitude difference (no longitude in matrix)",
    "Graha Yuddha (exact)": "Needs raw inter-planet degree proximity",
    "Nakshatra Pada (exact)": "Needs raw Moon longitude within 13.33° nakshatra arc",
    "Navamsha (D9) chart": "Needs divisional chart computation from raw longitude",
    "Vedha (obstruction)": "Needs specific house relationship + classical table lookup",
}
for gap, reason in gaps.items():
    print(f"  ❌ {gap:<30} → {reason}")

print(f"\n SOLUTION: Rebuild genesis_9000_MUNDANE.parquet with raw longitudes")
print(f"  The matrix builder should output T_X_Longitude for all planets.")
print(f"  With raw longitudes, ALL remaining features can be computed in <1 hour.")

# Print current NYSE Dasha
today_dasha = compute_dasha(date.today())
maha_name  = DASHA_ORDER[today_dasha["dasha_maha"]]
antar_name = DASHA_ORDER[today_dasha["dasha_antar"]]
prat_name  = DASHA_ORDER[today_dasha["dasha_prat"]]
print(f"\n{'='*70}")
print(f" NYSE DASHA TODAY ({date.today()})")
print(f"{'='*70}")
print(f"  Maha Dasha  : {maha_name} ({today_dasha['dasha_maha_frac']*100:.1f}% elapsed)")
print(f"  Antardasha  : {antar_name} ({today_dasha['dasha_antar_frac']*100:.1f}% elapsed)")
print(f"  Pratyantar  : {prat_name}")
print()
INTERP = {
    "Mercury": "Technology & communications dominance",
    "Jupiter": "Expansion, global finance, optimism",
    "Saturn":  "Contraction, old economy, austerity",
    "Venus":   "Luxury, real estate, consumer boom",
    "Mars":    "Energy, metals, conflict-driven volatility",
    "Rahu":    "Speculation, foreign assets, disruption",
    "Ketu":    "Dissolution, crypto-like assets, spiritual retreat",
    "Moon":    "Mass psychology, consumer-driven markets",
    "Sun":     "Government/policy dominant, leadership markets",
}
BEST_ETFS = {
    "Mercury":  "QQQ, XLC, HACK, SMH (tech/comms)",
    "Jupiter":  "JETS, XLF, GLD (aviation/finance/gold)",
    "Saturn":   "XLU, TLT, PAVE (utilities/bonds/infrastructure)",
    "Venus":    "XLP, XLRE, GLD (staples/real estate/gold)",
    "Mars":     "COPX, XME, XLE, SLV, UNG (metals/energy)",
    "Rahu":     "EEM, ARKK, USO (emerging/disruptive/oil)",
    "Moon":     "DBA, SLV, XLP (agriculture/silver/staples)",
}
print(f"  {maha_name} Maha: {INTERP[maha_name]}")
print(f"  {antar_name} Antar: {INTERP[antar_name]} (sub-theme)")
print(f"  Best sectors NOW: {BEST_ETFS.get(maha_name,'?')}")
print(f"  {antar_name} sub-theme adds: {BEST_ETFS.get(antar_name,'?')}")
print()
print(f"  IMPLICATION: We are in Mercury Dasha → {antar_name} Antardasha.")
print(f"  This means: {maha_name} assets lead, but {antar_name} assets are the")
print(f"  catalyst/sub-trend. Watch {antar_name}-ruled sectors for specific signals.")
