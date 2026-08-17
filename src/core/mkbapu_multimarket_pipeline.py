"""
Multi-Market MK Bapu Pipeline -- Brutal Multipoint Inspection
=============================================================
Markets: SPY / QQQ / DIA  (US, NYSE/NASDAQ)
         NIFTY / BANKNIFTY (India, NSE)

Key correctness decisions:
  1. Ascendant is LOCATION-DEPENDENT.
     - US markets   : NYSE  Lat=40.7128, Lon=-74.0060
     - Indian markets: NSE   Lat=19.0176, Lon=72.8561
  2. Market hours in UTC:
     - US    : 13:30-20:00 UTC  (9:30 AM - 4:00 PM ET)
     - India : 03:45-10:00 UTC  (9:15 AM - 3:30 PM IST)
  3. Bars per day:
     - US    : 26 bars  (390 min / 15)
     - India : 25 bars  (375 min / 15)
  4. Triple-Barrier horizons tuned per market volatility.
  5. Granger causality + SHAP + HMM regime on every asset.
"""
import sys, os, warnings, time, json
import numpy as np
import pandas as pd
import yfinance as yf
import swisseph as swe
from datetime import datetime, timezone

warnings.filterwarnings("ignore")

SCRATCH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
OUTPUT_DIR = os.path.join(SCRATCH, "mkbapu_multimarket_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

RASHI_NAMES = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"
]
RASHI_BIAS = {
    "Mithuna": +1, "Karka": +1, "Vrishchika": +1, "Meena": +1,
    "Vrishabha": -1, "Simha": -1, "Kanya": -1,
    "Makara": -1, "Kumbha": -1, "Mesha": -1,
    "Tula": 0, "Dhanu": 0
}

# ── Market Configs ──────────────────────────────────────────────────────────
MARKETS = {
    "US": {
        "assets": {
            "SPY": "SPY",
            "QQQ": "QQQ",
            "DIA": "DIA",
        },
        "lat": 40.7128, "lon": -74.0060,
        "utc_hour_start": 13, "utc_hour_end": 20,
        "expected_bars_per_day": 26,
        "pt_pct": 0.003, "sl_pct": 0.002, "barrier_bars": 4,
        "label": "NYSE (New York)"
    },
    "India": {
        "assets": {
            "NIFTY": "^NSEI",
            "BANKNIFTY": "^NSEBANK",
        },
        "lat": 19.0176, "lon": 72.8561,
        "utc_hour_start": 3, "utc_hour_end": 10,
        "expected_bars_per_day": 25,
        "pt_pct": 0.004, "sl_pct": 0.0025, "barrier_bars": 4,
        "label": "NSE (Mumbai)"
    }
}

# ═══════════════════════════════════════════════════════════════════════
# INSPECTION CHECKPOINT PRINTER
# ═══════════════════════════════════════════════════════════════════════
PASS = "[PASS]"
FAIL = "[FAIL]"
WARN = "[WARN]"

def checkpoint(step_num, title, checks):
    print(f"\n{'='*70}")
    print(f"  CHECKPOINT {step_num}: {title}")
    print(f"{'='*70}")
    all_ok = True
    for label, ok, detail in checks:
        status = PASS if ok else FAIL
        if ok is None:
            status = WARN
        print(f"  {status}  {label}")
        if detail:
            print(f"         {detail}")
        if not ok and ok is not None:
            all_ok = False
    print(f"  {'--- ALL CHECKS PASSED ---' if all_ok else '*** SOME CHECKS FAILED ***'}")
    return all_ok

# ═══════════════════════════════════════════════════════════════════════
# STEP 0: EPHEMERIS SELF-TEST (Against MK Bapu's known reference)
# ═══════════════════════════════════════════════════════════════════════
def ephemeris_self_test():
    print("\n" + "="*70)
    print("  STEP 0: EPHEMERIS SELF-TEST (Reference: MK Bapu Pine Script)")
    print("="*70)

    swe.set_ephe_path('')
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    # MK Bapu says: May 25 2026 05:03 Dubai => Vrishabha Lagna
    # Dubai = UTC+4, so 05:03 Dubai = 01:03 UTC
    dt_utc = datetime(2026, 5, 25, 1, 3, 0, tzinfo=timezone.utc)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                    dt_utc.hour + dt_utc.minute/60.0)

    checks = []
    for loc_label, lat, lon, expected in [
        ("Dubai (MK Bapu ref)", 25.2048, 55.2708, "Vrishabha"),
        ("NYSE (New York)",     40.7128, -74.0060, None),
        ("NSE  (Mumbai)",       19.0176,  72.8561, None),
    ]:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        asc_deg = ascmc[0]
        rashi = RASHI_NAMES[int(asc_deg / 30) % 12]
        if expected:
            ok = (rashi == expected)
            detail = f"Asc={asc_deg:.2f} deg -> {rashi} (expected {expected})"
        else:
            ok = None  # informational
            detail = f"Asc={asc_deg:.2f} deg -> {rashi} (different from Dubai!)"
        checks.append((loc_label, ok, detail))

    checkpoint(0, "EPHEMERIS REFERENCE VERIFICATION", checks)
    print("\n  CRITICAL: Each market uses its own exchange coordinates.")
    print("  US markets use NYSE lat/lon. Indian markets use NSE lat/lon.")
    return True


# ═══════════════════════════════════════════════════════════════════════
# STEP 1: FETCH & VALIDATE MARKET DATA
# ═══════════════════════════════════════════════════════════════════════
def fetch_and_validate(asset_name, ticker, cfg):
    print(f"\n  Fetching {asset_name} ({ticker})...")
    df = yf.download(ticker, interval="15m", period="60d", progress=False, auto_adjust=False)
    if df.empty:
        print(f"  {FAIL} Empty data for {ticker}")
        return None
    df = df.reset_index()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]

    col = 'Datetime' if 'Datetime' in df.columns else df.columns[0]
    df = df.rename(columns={col: 'dt'})
    df['dt'] = pd.to_datetime(df['dt'])
    if df['dt'].dt.tz is None:
        df['dt'] = df['dt'].dt.tz_localize('UTC')
    else:
        df['dt'] = df['dt'].dt.tz_convert('UTC')

    raw_count = len(df)

    # Filter market hours
    h = df['dt'].dt.hour
    m = df['dt'].dt.minute
    h_start = cfg['utc_hour_start']
    h_end   = cfg['utc_hour_end']
    mask = (h > h_start) | ((h == h_start) & (m >= 0))
    mask &= (h < h_end)
    df = df[mask].sort_values('dt').reset_index(drop=True)

    # Per-day bar count
    df['_date'] = df['dt'].dt.date
    daily_counts = df.groupby('_date').size()
    expected = cfg['expected_bars_per_day']

    # NaN check
    nan_cells = df[['Open','High','Low','Close','Volume']].isna().sum().sum()

    # Stale price check (consecutive identical closes)
    stale = (df['Close'].diff() == 0).sum()

    # Zero/negative price check
    bad_prices = (df['Close'] <= 0).sum()

    # Gap check (intra-session gap > 30min, < 300min)
    dt_diff_min = df['dt'].diff().dt.total_seconds().fillna(0) / 60
    large_gaps = ((dt_diff_min > 30) & (dt_diff_min < 300)).sum()

    checks = [
        ("Rows after market-hours filter", len(df) > 100,
         f"{raw_count} raw -> {len(df)} market-hours rows"),
        ("No NaN in OHLCV", nan_cells == 0,
         f"{nan_cells} NaN cells found"),
        ("No zero/negative prices", bad_prices == 0,
         f"{bad_prices} bad price rows"),
        ("Stale prices acceptable", stale < len(df) * 0.05,
         f"{stale} consecutive identical closes ({stale/len(df)*100:.1f}%)"),
        ("Intra-session gaps acceptable", large_gaps < 20,
         f"{large_gaps} intra-session gaps >30min"),
        ("Min bars/day acceptable", daily_counts.min() >= expected * 0.5,
         f"min={daily_counts.min()}, max={daily_counts.max()}, mean={daily_counts.mean():.1f} (expected ~{expected})"),
        ("Trading days count", len(daily_counts) >= 40,
         f"{len(daily_counts)} trading days from {df['dt'].min().date()} to {df['dt'].max().date()}"),
    ]
    checkpoint(f"1-{asset_name}", f"DATA QUALITY: {asset_name}", checks)
    df.drop(columns=['_date'], inplace=True)
    return df


# ═══════════════════════════════════════════════════════════════════════
# STEP 2: COMPUTE EPHEMERIS FEATURES PER BAR
# ═══════════════════════════════════════════════════════════════════════
def compute_bar_features(dt_utc, lat, lon):
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                    dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0)
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED | swe.FLG_SWIEPH
    feats = {}

    for pid, name in [(swe.SUN,"Sun"),(swe.MOON,"Moon"),(swe.MERCURY,"Mercury"),
                      (swe.VENUS,"Venus"),(swe.MARS,"Mars"),(swe.JUPITER,"Jupiter"),
                      (swe.SATURN,"Saturn"),(swe.URANUS,"Uranus"),(swe.NEPTUNE,"Neptune")]:
        r = swe.calc_ut(jd, pid, flags)
        lon2, speed = r[0][0], r[0][3]
        nak = int(lon2 / (360/27))
        feats[f"{name}_lon"]         = lon2
        feats[f"{name}_lon_sin"]     = np.sin(np.radians(lon2))
        feats[f"{name}_lon_cos"]     = np.cos(np.radians(lon2))
        feats[f"{name}_speed"]       = speed
        feats[f"{name}_retro"]       = 1.0 if speed < 0 else 0.0
        feats[f"{name}_sign"]        = int(lon2 / 30)
        feats[f"{name}_deg_in_sign"] = lon2 % 30
        feats[f"{name}_nak"]         = nak
        feats[f"{name}_nak_sin"]     = np.sin(2*np.pi*nak/27)
        feats[f"{name}_nak_cos"]     = np.cos(2*np.pi*nak/27)
        feats[f"{name}_pada"]        = int((lon2 % (360/27)) / (360/108)) + 1

    rahu_r = swe.calc_ut(jd, swe.MEAN_NODE, flags)
    rl = rahu_r[0][0]
    kl = (rl + 180) % 360
    feats["Rahu_lon"] = rl; feats["Rahu_sign"] = int(rl/30); feats["Rahu_nak"] = int(rl/(360/27))
    feats["Ketu_lon"] = kl; feats["Ketu_sign"] = int(kl/30); feats["Ketu_nak"] = int(kl/(360/27))

    # Key aspects
    lons = {n: feats[f"{n}_lon"] for n in ["Sun","Moon","Mercury","Venus","Mars",
                                            "Jupiter","Saturn","Uranus","Neptune"]}
    lons["Rahu"] = rl; lons["Ketu"] = kl
    pairs = [("Sun","Moon"),("Sun","Mars"),("Sun","Jupiter"),("Sun","Saturn"),
             ("Sun","Rahu"),("Moon","Mars"),("Moon","Jupiter"),("Moon","Saturn"),
             ("Moon","Rahu"),("Moon","Ketu"),("Mars","Saturn"),("Jupiter","Saturn"),
             ("Jupiter","Rahu"),("Saturn","Rahu"),("Mercury","Venus"),
             ("Venus","Jupiter"),("Mars","Jupiter")]
    for p1, p2 in pairs:
        if p1 in lons and p2 in lons:
            diff = abs(lons[p1] - lons[p2]) % 360
            diff = min(diff, 360 - diff)
            feats[f"asp_{p1}_{p2}_dist"] = diff
            for target, aname in [(0,"conj"),(60,"sext"),(90,"sqr"),(120,"tri"),(180,"opp")]:
                d = abs(diff - target)
                feats[f"asp_{p1}_{p2}_{aname}"] = max(0.0, 1.0 - d/8.0) if d <= 8 else 0.0

    # Panchang
    sun_l = feats["Sun_lon"]; moon_l = feats["Moon_lon"]
    elong = (moon_l - sun_l) % 360
    tithi = int(elong/12) + 1
    yoga  = int(((sun_l + moon_l) % 360) / (360/27)) + 1
    feats["tithi"] = tithi
    feats["tithi_sin"] = np.sin(2*np.pi*tithi/30)
    feats["tithi_cos"] = np.cos(2*np.pi*tithi/30)
    feats["moon_phase"] = elong/360.0
    feats["yoga"] = yoga
    feats["yoga_sin"] = np.sin(2*np.pi*yoga/27)
    feats["yoga_cos"] = np.cos(2*np.pi*yoga/27)

    # Ascendant (location-specific)
    try:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        asc = ascmc[0]
        feats["house_placidus_1_cusp"] = asc
        feats["asc_lon_sin"]  = np.sin(np.radians(asc))
        feats["asc_lon_cos"]  = np.cos(np.radians(asc))
        feats["asc_sign"]     = int(asc/30) % 12
        feats["asc_deg"]      = asc % 30
        # D9 Navamsha of Ascendant (changes every ~13 min)
        asc_d9 = (int(asc/30)*9 + int((asc%30)*9/30)) % 12
        feats["asc_d9_sign"] = asc_d9
        feats["asc_d9_sin"]  = np.sin(2*np.pi*asc_d9/12)
        feats["asc_d9_cos"]  = np.cos(2*np.pi*asc_d9/12)
        # D60 Shashtiamsha of Ascendant (changes every ~2 min, ultra-sensitive)
        asc_d60 = (int(asc/30)*60 + int((asc%30)*60/30)) % 12
        feats["asc_d60_sign"] = asc_d60
        feats["asc_d60_sin"]  = np.sin(2*np.pi*asc_d60/12)
        feats["asc_d60_cos"]  = np.cos(2*np.pi*asc_d60/12)
    except Exception:
        for k in ["house_placidus_1_cusp","asc_lon_sin","asc_lon_cos",
                  "asc_sign","asc_deg","asc_d9_sign","asc_d9_sin","asc_d9_cos",
                  "asc_d60_sign","asc_d60_sin","asc_d60_cos"]:
            feats[k] = 0.0

    # Temporal
    hf = dt_utc.hour + dt_utc.minute/60.0
    feats["hour_sin"]      = np.sin(2*np.pi*hf/24)
    feats["hour_cos"]      = np.cos(2*np.pi*hf/24)
    feats["day_of_week"]   = dt_utc.weekday()
    feats["dow_sin"]       = np.sin(2*np.pi*dt_utc.weekday()/5)
    feats["dow_cos"]       = np.cos(2*np.pi*dt_utc.weekday()/5)
    doy = dt_utc.timetuple().tm_yday
    feats["doy_sin"]       = np.sin(2*np.pi*doy/365.25636042)
    feats["doy_cos"]       = np.cos(2*np.pi*doy/365.25636042)

    return feats


def build_ephemeris_matrix(df, lat, lon, asset_name):
    print(f"    Computing ephemeris features for {len(df)} bars...")
    t0 = time.time()
    rows = []
    for i, row in df.iterrows():
        dt_utc = row['dt'].to_pydatetime()
        if dt_utc.tzinfo is None:
            dt_utc = dt_utc.replace(tzinfo=timezone.utc)
        rows.append(compute_bar_features(dt_utc, lat, lon))
        if (i+1) % 500 == 0:
            print(f"      {i+1}/{len(df)} bars ({time.time()-t0:.1f}s)")

    feat_df = pd.DataFrame(rows)

    # VALIDATION: Spot-check Ascendant sign matches expected rashi change frequency
    asc_sign_changes = (feat_df['asc_sign'].diff() != 0).sum()
    bars_per_change  = len(feat_df) / max(asc_sign_changes, 1)
    expected_bars    = 8  # ~2hr / 15min = 8 bars per rashi in US; ~8 in India

    checks = [
        ("Feature count consistent", len(feat_df.columns) > 150,
         f"{len(feat_df.columns)} features generated"),
        ("No NaN in ephemeris", feat_df.isna().sum().sum() == 0,
         f"{feat_df.isna().sum().sum()} NaN values"),
        ("Ascendant sign changes present", asc_sign_changes > 5,
         f"{asc_sign_changes} sign changes, {bars_per_change:.1f} bars/change (expected ~{expected_bars})"),
        ("Ascendant degree in [0,360)", (feat_df['house_placidus_1_cusp'].between(0,360)).all(),
         f"Range: {feat_df['house_placidus_1_cusp'].min():.1f} - {feat_df['house_placidus_1_cusp'].max():.1f}"),
        ("Moon nakshatra in [0,26]", feat_df['Moon_nak'].between(0,26).all(),
         f"Range: {feat_df['Moon_nak'].min()} - {feat_df['Moon_nak'].max()}"),
    ]
    checkpoint(f"2-{asset_name}", f"EPHEMERIS MATRIX: {asset_name}", checks)
    return feat_df


# ═══════════════════════════════════════════════════════════════════════
# STEP 3: MK BAPU FEATURES WITH VALIDATION
# ═══════════════════════════════════════════════════════════════════════
def apply_mkbapu_features(df, feat_df, asset_name):
    df2 = pd.concat([df.reset_index(drop=True), feat_df.reset_index(drop=True)], axis=1)

    asc_sign = feat_df['asc_sign'].values
    df2['mkb_rashi_idx']   = asc_sign
    df2['mkb_rashi_name']  = [RASHI_NAMES[x % 12] for x in asc_sign]
    df2['mkb_rashi_bias']  = [RASHI_BIAS.get(RASHI_NAMES[x % 12], 0) for x in asc_sign]

    # Feature 1: Rashi Changed
    changed = np.zeros(len(df2), dtype=np.int8)
    changed[0] = 1
    for i in range(1, len(df2)):
        changed[i] = 1 if asc_sign[i] != asc_sign[i-1] else 0
    df2['mkb_rashi_changed'] = changed

    # Feature 2: Rashi Start Price (Open at transit bar, normalised by prev close)
    rsp, current_rsp = [], df2['Open'].iloc[0]
    for i in range(len(df2)):
        if changed[i]:
            current_rsp = df2['Open'].iloc[i]
        rsp.append(current_rsp)
    df2['mkb_rashi_start_price'] = rsp

    # Feature 3: Distance to Rashi Start Price (normalised by 26-bar ATR)
    atr = (df2['High'] - df2['Low']).rolling(26, min_periods=1).mean().fillna(1.0)
    df2['mkb_dist_to_rashi'] = (df2['Close'] - df2['mkb_rashi_start_price']) / (atr + 1e-9)

    # Feature 4: Bars Since Rashi Change (capped at 16)
    bs, counter = [], 0
    for i in range(len(df2)):
        counter = 0 if changed[i] else counter + 1
        bs.append(min(counter, 16))
    df2['mkb_bars_since_rashi']      = bs
    df2['mkb_bars_since_rashi_norm'] = np.array(bs) / 8.0

    # Feature 5: Fraction of Rashi window elapsed (deg in sign / 30)
    df2['mkb_rashi_pct_elapsed'] = feat_df['asc_deg'].values / 30.0

    # Feature 6: Vrishchika Pushkar (60 min after Vrishchika start)
    pushkar_prices, pushkar_active = [], []
    vrishchika_start_time, pushkar_price = None, None
    for i in range(len(df2)):
        dt = df2['dt'].iloc[i]
        if changed[i]:
            pushkar_price = None
            vrishchika_start_time = dt if df2['mkb_rashi_name'].iloc[i] == 'Vrishchika' else None
        if vrishchika_start_time is not None:
            mins = (dt - vrishchika_start_time).total_seconds() / 60.0
            if mins >= 60.0 and pushkar_price is None:
                pushkar_price = df2['Open'].iloc[i]
        pushkar_prices.append(pushkar_price if pushkar_price is not None else np.nan)
        pushkar_active.append(1 if pushkar_price is not None else 0)
    df2['mkb_pushkar_price']  = pushkar_prices
    df2['mkb_pushkar_active'] = pushkar_active
    df2['mkb_dist_to_pushkar'] = np.where(
        np.array(pushkar_active) == 1,
        (df2['Close'].values - np.array([x if x is not None else 0 for x in pushkar_prices])) / (atr.values + 1e-9),
        0.0
    )

    mkb_cols = [c for c in df2.columns if c.startswith('mkb_')]
    rashi_change_count = int(changed.sum())
    pushkar_windows = int(sum(1 for p in pushkar_active if p))
    vrishchika_count = (df2['mkb_rashi_name'] == 'Vrishchika').sum()

    checks = [
        ("Rashi changes plausible", 5 < rashi_change_count < 300,
         f"{rashi_change_count} rashi changes in dataset"),
        ("dist_to_rashi is finite", df2['mkb_dist_to_rashi'].isna().sum() == 0,
         f"NaN count: {df2['mkb_dist_to_rashi'].isna().sum()}"),
        ("bars_since_rashi in [0,16]", df2['mkb_bars_since_rashi'].between(0,16).all(),
         f"Range: {df2['mkb_bars_since_rashi'].min()} - {df2['mkb_bars_since_rashi'].max()}"),
        ("Pushkar window activates when Vrishchika present", vrishchika_count == 0 or pushkar_windows > 0,
         f"Vrishchika bars: {vrishchika_count}, Pushkar active bars: {pushkar_windows}"),
        ("All 10 MK Bapu features created", len(mkb_cols) == 10,
         f"{len(mkb_cols)} features: {mkb_cols}"),
    ]
    checkpoint(f"3-{asset_name}", f"MK BAPU FEATURES: {asset_name}", checks)
    return df2


# ═══════════════════════════════════════════════════════════════════════
# STEP 4: INTRADAY TRIPLE-BARRIER LABELING WITH VALIDATION
# ═══════════════════════════════════════════════════════════════════════
def apply_triple_barrier(df, pt_pct, sl_pct, barrier_bars, asset_name):
    closes = df['Close'].values
    highs  = df['High'].values
    lows   = df['Low'].values
    labels = np.zeros(len(closes), dtype=np.int8)

    for i in range(len(closes) - barrier_bars):
        entry  = closes[i]
        pt_lvl = entry * (1 + pt_pct)
        sl_lvl = entry * (1 - sl_pct)
        label  = 0
        for j in range(1, barrier_bars + 1):
            h = highs[i+j]; l = lows[i+j]
            if h >= pt_lvl:
                label =  1; break
            elif l <= sl_lvl:
                label = -1; break
        labels[i] = label
    labels[-barrier_bars:] = 0

    s = pd.Series(labels, index=df.index, name='label')
    dist = {-1: (labels==-1).sum(), 0: (labels==0).sum(), 1: (labels==1).sum()}
    n = len(labels)
    ratio_non_neutral = (dist[-1] + dist[1]) / max(n, 1)

    checks = [
        ("Labels generated", n > 100,
         f"{n} total bars labeled"),
        ("Has both Long and Short labels", dist[1] > 0 and dist[-1] > 0,
         f"Long={dist[1]}({dist[1]/n:.1%}), Short={dist[-1]}({dist[-1]/n:.1%}), Neutral={dist[0]}({dist[0]/n:.1%})"),
        ("Non-neutral ratio > 5%", ratio_non_neutral > 0.05,
         f"{ratio_non_neutral:.1%} actionable bars"),
        ("Barriers not too tight (some neutral)", dist[0] > n * 0.3,
         f"Neutral bars: {dist[0]} ({dist[0]/n:.1%}) -- should be >30% for realistic trading"),
        ("Long/Short ratio not extreme", 0.2 < dist[1]/(dist[-1]+1) < 5.0,
         f"Long:Short ratio = {dist[1]/(dist[-1]+1):.2f}"),
    ]
    checkpoint(f"4-{asset_name}", f"TRIPLE-BARRIER LABELS: {asset_name}", checks)
    return s


# ═══════════════════════════════════════════════════════════════════════
# STEP 5: GRANGER CAUSALITY
# ═══════════════════════════════════════════════════════════════════════
def granger_test(df, asset_name):
    print(f"\n  [Granger] {asset_name}: rashi_changed -> next-bar |return|")
    from statsmodels.tsa.stattools import grangercausalitytests
    import io, contextlib

    df2 = df.copy()
    df2['bar_ret']      = df2['Close'].pct_change().fillna(0)
    df2['next_bar_vol'] = df2['bar_ret'].abs().shift(-1)
    data = df2[['next_bar_vol', 'mkb_rashi_changed']].dropna().values

    results = {}
    try:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            gc = grangercausalitytests(data, maxlag=4, verbose=False)
        sig_any = False
        for lag, res in gc.items():
            p = res[0]['ssr_ftest'][1]
            results[f'lag{lag}_p'] = round(p, 6)
            sig = "[SIG p<0.05]" if p < 0.05 else "[not sig]  "
            print(f"    Lag {lag}: p={p:.4f}  {sig}")
            if p < 0.05:
                sig_any = True
        results['any_significant'] = sig_any
    except Exception as e:
        print(f"    Granger error: {e}")
        results['error'] = str(e)
    return results


# ═══════════════════════════════════════════════════════════════════════
# STEP 6: XGBOOST -- BASELINE vs AUGMENTED with 3-FOLD TIME-SERIES CV
# ═══════════════════════════════════════════════════════════════════════
def train_xgboost(df, labels, asset_name):
    print(f"\n  [XGBoost] {asset_name}: 3-Fold Time-Series CV")
    import xgboost as xgb
    from sklearn.metrics import accuracy_score, f1_score, precision_score

    drop_cols = {'dt','Open','High','Low','Close','Volume','label',
                 'mkb_rashi_name','mkb_rashi_start_price','mkb_pushkar_price',
                 'mkb_rashi_idx','_date'}

    df2 = df.copy()
    df2['label'] = labels
    df2 = df2.dropna(subset=['label'])
    df2 = df2[df2['label'] != 0].reset_index(drop=True)
    n = len(df2)

    if n < 100:
        print(f"    Insufficient labeled bars ({n}). Skipping.")
        return None

    y = (df2['label'] == 1).astype(int).values

    baseline_cols = [c for c in df2.columns
                     if c not in drop_cols
                     and not c.startswith('mkb_')
                     and not c.startswith('asc_rashi')
                     and pd.api.types.is_numeric_dtype(df2[c])]
    augmented_cols = baseline_cols + [c for c in df2.columns
                                      if c.startswith('mkb_')
                                      and pd.api.types.is_numeric_dtype(df2[c])]

    xgb_params = dict(
        n_estimators=300, max_depth=4, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.6, min_child_weight=5,
        tree_method='hist', nthread=4, random_state=42,
        use_label_encoder=False, eval_metric='logloss',
        early_stopping_rounds=20
    )

    results = {}
    fold_size = n // 3

    for mode, cols in [('baseline', baseline_cols), ('augmented', augmented_cols)]:
        X = df2[cols].fillna(0).values.astype(np.float32)
        fold_accs, fold_f1s, fold_precs = [], [], []

        for fold in range(3):
            train_end = fold_size * (fold + 1)
            test_start = train_end
            test_end   = min(train_end + fold_size, n)
            if test_end - test_start < 20:
                continue
            X_tr, X_te = X[:train_end], X[test_start:test_end]
            y_tr, y_te = y[:train_end], y[test_start:test_end]

            if len(np.unique(y_tr)) < 2 or len(np.unique(y_te)) < 2:
                continue

            clf = xgb.XGBClassifier(**xgb_params)
            clf.fit(X_tr, y_tr, eval_set=[(X_te, y_te)], verbose=False)
            y_pred = clf.predict(X_te)
            proba  = clf.predict_proba(X_te)[:, 1]
            top10  = proba >= np.percentile(proba, 90)

            fold_accs.append(accuracy_score(y_te, y_pred))
            fold_f1s.append(f1_score(y_te, y_pred, average='binary', zero_division=0))
            fold_precs.append(y_te[top10].mean() if top10.sum() > 0 else 0.5)

        # Final model on full 80% for SHAP
        split = int(n * 0.8)
        X_tr_f, X_te_f = X[:split], X[split:]
        y_tr_f, y_te_f = y[:split], y[split:]
        clf_final = xgb.XGBClassifier(**xgb_params)
        clf_final.fit(X_tr_f, y_tr_f, eval_set=[(X_te_f, y_te_f)], verbose=False)

        results[mode] = {
            'model': clf_final,
            'cols': cols,
            'acc':  round(np.mean(fold_accs),  4) if fold_accs  else 0.0,
            'f1':   round(np.mean(fold_f1s),   4) if fold_f1s   else 0.0,
            'prec': round(np.mean(fold_precs), 4) if fold_precs else 0.0,
            'X_test': X_te_f,
            'y_test': y_te_f,
            'n_features': len(cols),
            'n_samples': n,
        }
        print(f"    [{mode.upper():10s}] {len(cols):3d} feats | "
              f"Acc={results[mode]['acc']:.4f} | "
              f"F1={results[mode]['f1']:.4f} | "
              f"Top10%Prec={results[mode]['prec']:.4f}")

    if 'baseline' in results and 'augmented' in results:
        da = results['augmented']['acc']  - results['baseline']['acc']
        dp = results['augmented']['prec'] - results['baseline']['prec']
        verdict = "[WIN] MK BAPU ADDS EDGE" if (da > 0.005 or dp > 0.02) else "[FAIL] No incremental edge"
        print(f"    Delta Accuracy:    {da:+.4f}")
        print(f"    Delta Top10 Prec:  {dp:+.4f}")
        print(f"    VERDICT: {verdict}")
        results['verdict'] = verdict
        results['delta_acc'] = da
        results['delta_prec'] = dp

    return results


# ═══════════════════════════════════════════════════════════════════════
# STEP 7: SHAP ANALYSIS
# ═══════════════════════════════════════════════════════════════════════
def run_shap(results, asset_name, market_name):
    if not results or 'augmented' not in results:
        return
    try:
        import shap
    except ImportError:
        return

    model   = results['augmented']['model']
    cols    = results['augmented']['cols']
    X_test  = results['augmented']['X_test']

    sample_size = min(400, len(X_test))
    idx = np.random.RandomState(42).choice(len(X_test), sample_size, replace=False)
    X_shap = X_test[idx]

    explainer   = shap.TreeExplainer(model)
    shap_vals   = explainer.shap_values(X_shap)
    mean_shap   = np.abs(shap_vals).mean(axis=0)

    top20 = np.argsort(mean_shap)[::-1][:20]
    print(f"\n    --- SHAP Top 20: {asset_name} ---")
    for rank, i in enumerate(top20, 1):
        tag = "[MKB]" if cols[i].startswith('mkb_') else "     "
        print(f"    {rank:2d}. {tag} {cols[i]:<50s} {mean_shap[i]:.6f}")

    mkb_idxs = [i for i, c in enumerate(cols) if c.startswith('mkb_')]
    if mkb_idxs:
        print(f"\n    --- MK Bapu Feature SHAP Detail: {asset_name} ---")
        mkb_shap = sorted([(cols[i], mean_shap[i]) for i in mkb_idxs], key=lambda x: -x[1])
        for fname, sv in mkb_shap:
            pct = 100 * (mean_shap < sv).sum() / len(mean_shap)
            print(f"    {fname:<50s}  SHAP={sv:.6f}  (top {100-pct:.0f}th pct of all feats)")

    # Save plot
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(12, 8))
        top_names = [cols[i] for i in top20]
        top_vals  = [mean_shap[i] for i in top20]
        colors = ['#e74c3c' if n.startswith('mkb_') else '#2c3e50' for n in top_names]
        ax.barh(range(len(top_names)), top_vals[::-1], color=colors[::-1])
        ax.set_yticks(range(len(top_names)))
        ax.set_yticklabels(top_names[::-1], fontsize=8)
        ax.set_xlabel("Mean |SHAP|")
        ax.set_title(f"Feature Importance: {asset_name} ({market_name}) | RED=MK Bapu features")
        plt.tight_layout()
        path = os.path.join(OUTPUT_DIR, f"shap_{market_name}_{asset_name}.png")
        plt.savefig(path, dpi=150)
        plt.close()
        print(f"    SHAP plot: {path}")
    except Exception as e:
        print(f"    Plot error: {e}")


# ═══════════════════════════════════════════════════════════════════════
# STEP 8: HMM REGIME BACKTEST
# ═══════════════════════════════════════════════════════════════════════
def regime_backtest(df, labels, results, asset_name):
    if not results or 'augmented' not in results:
        return
    try:
        from hmmlearn.hmm import GaussianHMM
    except ImportError:
        print("    hmmlearn not available")
        return

    model = results['augmented']['model']
    cols  = results['augmented']['cols']

    df2 = df.copy()
    df2['label'] = labels
    df2 = df2.dropna(subset=['label'])
    df2 = df2[df2['label'] != 0].reset_index(drop=True)
    n = len(df2)
    if n < 80:
        return

    # FATAL BUG FIX: Shift pct_change by -1 to capture FORWARD returns
    bar_rets = df2['Close'].pct_change().shift(-1).fillna(0).values
    log_vol  = np.log(df2['High'] / df2['Low'].clip(lower=1e-9)).fillna(0).values
    obs = np.column_stack([bar_rets, log_vol])

    hmm = GaussianHMM(n_components=3, covariance_type='diag',
                      n_iter=100, random_state=42)
    hmm.fit(obs)
    regimes = hmm.predict(obs)

    split    = int(n * 0.8)
    X_test   = df2[cols].fillna(0).values.astype(np.float32)[split:]
    rets_te  = bar_rets[split:]
    reg_te   = regimes[split:]
    proba    = model.predict_proba(X_test)[:, 1]
    signal   = np.where(proba > 0.55, 1, np.where(proba < 0.45, -1, 0))

    # Sort regimes by mean log-vol
    regime_vols = [obs[split:][reg_te == r, 1].mean() if (reg_te==r).sum() > 0 else 0 for r in range(3)]
    order = np.argsort(regime_vols)
    names = {order[0]: "Low-Vol", order[1]: "Med-Vol", order[2]: "High-Vol"}

    print(f"\n    --- HMM Regime Backtest: {asset_name} ---")
    
    # FULL BACKTEST STATS
    full_strat = rets_te * signal
    active_mask = signal != 0
    active_rets = full_strat[active_mask]
    
    if len(active_rets) > 0:
        cum_rets = (1 + full_strat).cumprod()
        tot_ret = cum_rets[-1] - 1
        
        # Drawdown
        roll_max = np.maximum.accumulate(cum_rets)
        drawdowns = (cum_rets - roll_max) / roll_max
        max_dd = drawdowns.min()
        
        # Annualized CAGR
        years = max((df2['dt'].iloc[-1] - df2['dt'].iloc[split]).total_seconds() / (365.25636042*24*3600), 0.01)
        cagr = (1 + tot_ret)**(1/years) - 1
        
        wr = (active_rets > 0).mean()
        wins = active_rets[active_rets > 0]
        losses = active_rets[active_rets < 0]
        pf = abs(wins.sum() / losses.sum()) if len(losses) > 0 and losses.sum() != 0 else np.inf
        
        print(f"    [FULL TEST SET] Trades={len(active_rets):3d} | TotalRet={tot_ret*100:+.2f}% | CAGR={cagr*100:+.1f}% | MaxDD={max_dd*100:.1f}% | WinRate={wr*100:.1f}% | ProfitFactor={pf:.2f}")
    else:
        print("    [FULL TEST SET] No trades triggered.")

    for r in range(3):
        mask = reg_te == r
        if mask.sum() < 5:
            continue
        strat = rets_te[mask] * signal[mask]
        active = signal[mask] != 0
        active_rets = rets_te[mask][active] * signal[mask][active]
        wr = (active_rets > 0).mean() if active.sum() > 0 else 0
        sr = (strat.mean() / (strat.std()+1e-9)) * np.sqrt(252 * 26)
        print(f"    {names.get(r,'Reg'+str(r)):10s}  n={mask.sum():4d}  "
              f"Trades={active.sum():3d}  WinRate={wr:.1%}  AnnSharpe={sr:+.2f}")


# ═══════════════════════════════════════════════════════════════════════
# MASTER RUNNER
# ═══════════════════════════════════════════════════════════════════════
def run_asset(asset_name, ticker, market_name, cfg):
    print(f"\n\n{'#'*70}")
    print(f"#  ASSET: {asset_name} ({ticker}) | MARKET: {market_name}")
    print(f"{'#'*70}")

    swe.set_ephe_path('')
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    lat, lon = cfg['lat'], cfg['lon']

    # Step 1: Fetch & Validate
    df = fetch_and_validate(asset_name, ticker, cfg)
    if df is None:
        return None

    # Step 2: Ephemeris
    feat_df = build_ephemeris_matrix(df, lat, lon, asset_name)

    # Step 3: MK Bapu features
    df2 = apply_mkbapu_features(df, feat_df, asset_name)

    # Step 4: Triple-Barrier
    labels = apply_triple_barrier(df2, cfg['pt_pct'], cfg['sl_pct'],
                                  cfg['barrier_bars'], asset_name)

    # Step 5: Granger
    granger = granger_test(df2, asset_name)

    # Step 6: XGBoost
    xgb_results = train_xgboost(df2, labels, asset_name)

    # Step 7: SHAP
    run_shap(xgb_results, asset_name, market_name)

    # Step 8: HMM
    regime_backtest(df2, labels, xgb_results, asset_name)

    # Save output
    summary = {
        'asset': asset_name, 'market': market_name,
        'ticker': ticker, 'bars': len(df2),
        'granger_sig': granger.get('any_significant', False),
        'verdict': xgb_results.get('verdict', 'N/A') if xgb_results else 'N/A',
        'delta_acc':  xgb_results.get('delta_acc', 0) if xgb_results else 0,
        'delta_prec': xgb_results.get('delta_prec', 0) if xgb_results else 0,
    }
    return summary


def main():
    t0 = time.time()
    print("=" * 70)
    print("  MULTI-MARKET MK BAPU PIPELINE -- BRUTAL INSPECTION")
    print("  Markets: US (SPY/QQQ/DIA) + India (NIFTY/BANKNIFTY)")
    print("=" * 70)

    ephemeris_self_test()

    all_summaries = []
    for market_name, cfg in MARKETS.items():
        for asset_name, ticker in cfg['assets'].items():
            try:
                summary = run_asset(asset_name, ticker, market_name, cfg)
                if summary:
                    all_summaries.append(summary)
            except Exception as e:
                print(f"\n  ERROR in {asset_name}: {e}")
                import traceback
                traceback.print_exc()

    # Final summary table
    print(f"\n\n{'='*70}")
    print("  FINAL RESULTS SUMMARY -- ALL MARKETS")
    print(f"{'='*70}")
    print(f"  {'Asset':<12} {'Market':<7} {'Bars':<6} {'Granger':<9} {'DeltaAcc':>9} {'DeltaPrec':>10} Verdict")
    print(f"  {'-'*68}")
    for s in all_summaries:
        gr = "SIG" if s['granger_sig'] else "no "
        print(f"  {s['asset']:<12} {s['market']:<7} {s['bars']:<6} {gr:<9} "
              f"{s['delta_acc']:+9.4f} {s['delta_prec']:+10.4f}  {s['verdict']}")

    # Save JSON
    out_json = os.path.join(OUTPUT_DIR, "multimarket_results.json")
    with open(out_json, 'w') as f:
        json.dump(all_summaries, f, indent=2)

    total = time.time() - t0
    print(f"\n  Total runtime: {total/60:.1f} minutes")
    print(f"  Results saved: {out_json}")
    print("=" * 70)


if __name__ == "__main__":
    main()


# CRITICAL BUG FIX #17: Ensure swisseph is closed
import atexit
atexit.register(swe.close)
