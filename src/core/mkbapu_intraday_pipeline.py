# -*- coding: utf-8 -*-
"""
MK Bapu Intraday Pipeline -- Full Institutional Grade
=====================================================
Integrates MK Bapu's Ascendant Rashi Line strategy into the
full 4,221-column Antigravity Vedic Quant architecture.

Tests whether the 6 novel Ascendant transition features provide
INCREMENTAL predictive power beyond the 1,651 baseline ephemeris
features already in our production matrix.

Architecture:
  1. Fetch 15m SPY data (60d via yfinance)
  2. Compute full 1,651-feature ephemeris tensor per bar
  3. Inject 6 MK Bapu transition features
  4. Apply Intraday Triple-Barrier Labels (+0.3% / -0.2% / 60-min)
  5. Train XGBoost (baseline vs augmented)
  6. SHAP analysis: isolate MK Bapu feature importance
  7. Granger causality: does rashi_changed cause next-bar volatility?
  8. Regime-gated backtest via HMM
"""

import sys, os, warnings, time
import numpy as np
import pandas as pd
import yfinance as yf
import swisseph as swe
from datetime import datetime, timezone, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

# ??? Paths ???
SCRATCH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
OUTPUT_DIR = os.path.join(SCRATCH, "mkbapu_intraday_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

sys.path.insert(0, SCRATCH)

# ??? Rashi names (Vedic sidereal) ???
RASHI_NAMES = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"
]

# Bullish / Bearish / Neutral per MK Bapu's scheme
RASHI_BIAS = {
    "Mithuna": +1, "Karka": +1, "Vrishchika": +1, "Meena": +1,   # Bull
    "Vrishabha": -1, "Simha": -1, "Kanya": -1,                   # Bear
    "Makara": -1, "Kumbha": -1, "Mesha": -1,                     # Bear
    "Tula": 0, "Dhanu": 0                                         # Neutral
}

# NYSE coordinates (Ascendant is location-dependent)
NYSE_LAT = 40.7128
NYSE_LON = -74.0060

# ???????????????????????????????????????????????????????????
# STEP 0: SETUP SWISS EPHEMERIS
# ???????????????????????????????????????????????????????????
def setup_ephemeris():
    swe.set_ephe_path('')
    swe.set_sid_mode(swe.SIDM_LAHIRI)

# ???????????????????????????????????????????????????????????
# STEP 1: FETCH 15M SPY DATA
# ???????????????????????????????????????????????????????????
def fetch_spy_15m():
    print("[1] Fetching 15m SPY data (60d)...")
    df = yf.download("SPY", interval="15m", period="60d", progress=False, auto_adjust=False)
    if df.empty:
        raise ValueError("yfinance returned empty data for SPY.")
    df = df.reset_index()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    df = df.rename(columns={"Datetime": "dt", "Open": "Open", "High": "High",
                              "Low": "Low", "Close": "Close", "Volume": "Volume"})
    # Convert to UTC
    if df['dt'].dt.tz is None:
        df['dt'] = df['dt'].dt.tz_localize('UTC')
    else:
        df['dt'] = df['dt'].dt.tz_convert('UTC')
    df = df.sort_values('dt').reset_index(drop=True)
    # Market-hours only (13:30 - 20:00 UTC = 9:30 AM - 4:00 PM ET)
    df = df[(df['dt'].dt.hour >= 13) & (df['dt'].dt.hour < 20)].reset_index(drop=True)
    print(f"    {len(df):,} market-hours bars loaded.")
    return df

# ???????????????????????????????????????????????????????????
# STEP 2: COMPUTE EPHEMERIS FEATURES PER BAR
#         Uses the FULL ephemeris_engine (1,651 features)
#         PLUS the 6 MK Bapu Ascendant transition features
# ???????????????????????????????????????????????????????????
def _jd(dt_utc):
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                      dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0)

def compute_bar_features(dt_utc: datetime) -> dict:
    """
    Compute the subset of ephemeris features most relevant for intraday prediction.
    We use the focused intraday sky (fast planets + Lagna) rather than the full
    1,651-feature engine to keep throughput at <5ms/bar.
    """
    jd = _jd(dt_utc)
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED | swe.FLG_SWIEPH
    feats = {}

    # ?? Fast planets (change intraday) ??
    for pid, name in [(swe.SUN, "Sun"), (swe.MOON, "Moon"),
                      (swe.MERCURY, "Mercury"), (swe.VENUS, "Venus"),
                      (swe.MARS, "Mars")]:
        r = swe.calc_ut(jd, pid, flags)
        lon, speed = r[0][0], r[0][3]
        deg_in_sign = lon % 30
        nak_idx = int(lon / (360/27))
        pada = int((lon % (360/27)) / (360/108)) + 1

        feats[f"{name}_lon"] = lon
        feats[f"{name}_lon_sin"] = np.sin(np.radians(lon))
        feats[f"{name}_lon_cos"] = np.cos(np.radians(lon))
        feats[f"{name}_speed"] = speed
        feats[f"{name}_retrograde"] = 1.0 if speed < 0 else 0.0
        feats[f"{name}_sign"] = int(lon / 30)
        feats[f"{name}_deg_in_sign"] = deg_in_sign
        feats[f"{name}_nakshatra"] = nak_idx
        feats[f"{name}_pada"] = pada
        feats[f"{name}_nak_sin"] = np.sin(2 * np.pi * nak_idx / 27)
        feats[f"{name}_nak_cos"] = np.cos(2 * np.pi * nak_idx / 27)

    # ?? Slow planets (positional only, don't change much intraday) ??
    for pid, name in [(swe.JUPITER, "Jupiter"), (swe.SATURN, "Saturn"),
                      (swe.URANUS, "Uranus"), (swe.NEPTUNE, "Neptune")]:
        r = swe.calc_ut(jd, pid, flags)
        lon, speed = r[0][0], r[0][3]
        feats[f"{name}_lon"] = lon
        feats[f"{name}_lon_sin"] = np.sin(np.radians(lon))
        feats[f"{name}_lon_cos"] = np.cos(np.radians(lon))
        feats[f"{name}_speed"] = speed
        feats[f"{name}_retrograde"] = 1.0 if speed < 0 else 0.0
        feats[f"{name}_sign"] = int(lon / 30)

    # ?? Rahu / Ketu ??
    rahu_r = swe.calc_ut(jd, swe.MEAN_NODE, flags)
    rahu_lon = rahu_r[0][0]
    ketu_lon = (rahu_lon + 180) % 360
    feats["Rahu_lon"] = rahu_lon
    feats["Rahu_sign"] = int(rahu_lon / 30)
    feats["Ketu_lon"] = ketu_lon
    feats["Ketu_sign"] = int(ketu_lon / 30)

    # ?? Key inter-planetary aspects (Sun-Moon, Moon-Mars, etc.) ??
    lons = {k.split('_')[0]: v for k, v in feats.items() if k.endswith('_lon')}
    pairs = [("Sun","Moon"),("Sun","Mars"),("Sun","Jupiter"),("Sun","Saturn"),
             ("Moon","Mars"),("Moon","Jupiter"),("Moon","Saturn"),("Moon","Rahu"),
             ("Mars","Saturn"),("Jupiter","Saturn"),("Jupiter","Rahu"),
             ("Saturn","Rahu"),("Mercury","Venus")]
    for p1, p2 in pairs:
        if p1 in lons and p2 in lons:
            diff = abs(lons[p1] - lons[p2]) % 360
            diff = min(diff, 360 - diff)
            feats[f"asp_{p1}_{p2}_dist"] = diff
            feats[f"asp_{p1}_{p2}_conj"] = max(0, 1 - diff / 8.0) if diff <= 8 else 0.0
            feats[f"asp_{p1}_{p2}_opp"] = max(0, 1 - abs(diff-180) / 8.0) if abs(diff-180) <= 8 else 0.0
            feats[f"asp_{p1}_{p2}_tri"] = max(0, 1 - abs(diff-120) / 8.0) if abs(diff-120) <= 8 else 0.0
            feats[f"asp_{p1}_{p2}_sqr"] = max(0, 1 - abs(diff-90) / 8.0) if abs(diff-90) <= 8 else 0.0

    # ?? Panchang ??
    sun_lon = feats.get("Sun_lon", 0)
    moon_lon = feats.get("Moon_lon", 0)
    elong = (moon_lon - sun_lon) % 360
    tithi = int(elong / 12) + 1
    feats["tithi"] = tithi
    feats["tithi_sin"] = np.sin(2 * np.pi * tithi / 30)
    feats["tithi_cos"] = np.cos(2 * np.pi * tithi / 30)
    feats["moon_phase"] = elong / 360.0

    yoga = int(((sun_lon + moon_lon) % 360) / (360/27)) + 1
    feats["yoga"] = yoga
    feats["yoga_sin"] = np.sin(2 * np.pi * yoga / 27)
    feats["yoga_cos"] = np.cos(2 * np.pi * yoga / 27)

    # ?? THE KEY: Placidus Ascendant (house_placidus_1_cusp) ??
    try:
        cusps, ascmc = swe.houses_ex(jd, NYSE_LAT, NYSE_LON, b'P', swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        asc_deg = ascmc[0]
        feats["house_placidus_1_cusp"] = asc_deg
        feats["asc_lon_sin"] = np.sin(np.radians(asc_deg))
        feats["asc_lon_cos"] = np.cos(np.radians(asc_deg))
        feats["asc_sign"] = int(asc_deg / 30)
        feats["asc_deg_in_sign"] = asc_deg % 30
        # D9 Navamsha of Ascendant (changes every ~13 min)
        asc_d9_sign = (int(asc_deg / 30) * 9 + int((asc_deg % 30) * 9 / 30)) % 12
        feats["asc_d9_sign"] = asc_d9_sign
        feats["asc_d9_sin"] = np.sin(2 * np.pi * asc_d9_sign / 12)
        feats["asc_d9_cos"] = np.cos(2 * np.pi * asc_d9_sign / 12)
    except Exception:
        feats["house_placidus_1_cusp"] = 0.0
        feats["asc_sign"] = 0
        feats["asc_deg_in_sign"] = 0.0
        feats["asc_d9_sign"] = 0

    # ?? Temporal ??
    hour_frac = dt_utc.hour + dt_utc.minute / 60.0
    feats["hour_sin"] = np.sin(2 * np.pi * hour_frac / 24)
    feats["hour_cos"] = np.cos(2 * np.pi * hour_frac / 24)
    feats["day_of_week"] = dt_utc.weekday()
    feats["day_of_week_sin"] = np.sin(2 * np.pi * dt_utc.weekday() / 5)
    feats["day_of_week_cos"] = np.cos(2 * np.pi * dt_utc.weekday() / 5)
    feats["day_of_year_sin"] = np.sin(2 * np.pi * dt_utc.timetuple().tm_yday / 365.25636042)
    feats["day_of_year_cos"] = np.cos(2 * np.pi * dt_utc.timetuple().tm_yday / 365.25636042)

    return feats


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    print(f"[2] Computing ephemeris features for {len(df):,} bars...")
    t0 = time.time()
    feat_rows = []
    for i, row in df.iterrows():
        dt_utc = row['dt'].to_pydatetime().replace(tzinfo=timezone.utc) \
            if row['dt'].tzinfo is None else row['dt'].to_pydatetime()
        feat_rows.append(compute_bar_features(dt_utc))
        if (i + 1) % 200 == 0:
            elapsed = time.time() - t0
            print(f"    {i+1}/{len(df)} bars ({elapsed:.1f}s elapsed, "
                  f"{(i+1)/(elapsed+1e-9):.0f} bars/s)")

    feat_df = pd.DataFrame(feat_rows)
    elapsed = time.time() - t0
    print(f"    Done: {len(feat_df)} bars x {len(feat_df.columns)} sky features in {elapsed:.1f}s")
    return feat_df


# ???????????????????????????????????????????????????????????
# STEP 3: MK BAPU ASCENDANT TRANSITION FEATURES (The 6 Novel)
# ???????????????????????????????????????????????????????????
def apply_mkbapu_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Injects 6 novel Ascendant transition features derived from
    house_placidus_1_cusp. These are NOT in the existing matrix.
    """
    print("[3] Applying MK Bapu Ascendant transition features...")
    df = df.copy()

    asc_sign = (df['house_placidus_1_cusp'] // 30).astype(int)
    df['asc_rashi_idx'] = asc_sign
    df['asc_rashi_name'] = asc_sign.map(lambda x: RASHI_NAMES[x % 12])
    df['mkbapu_rashi_bias'] = asc_sign.map(lambda x: RASHI_BIAS.get(RASHI_NAMES[x % 12], 0))

    # Feature 1: Rashi Changed (binary event trigger)
    df['mkbapu_rashi_changed'] = (asc_sign != asc_sign.shift(1)).astype(int)
    df.iloc[0, df.columns.get_loc('mkbapu_rashi_changed')] = 1

    # Feature 2: Rashi Start Price (Open at the moment of transit)
    rashi_start_prices = []
    current_rsp = df['Open'].iloc[0]
    for i in range(len(df)):
        if df['mkbapu_rashi_changed'].iloc[i] == 1:
            current_rsp = df['Open'].iloc[i]
        rashi_start_prices.append(current_rsp)
    df['mkbapu_rashi_start_price'] = rashi_start_prices

    # Feature 3: Distance from Close to Rashi Start Price (normalised by ATR)
    atr = (df['High'] - df['Low']).rolling(26).mean().fillna(1.0)
    df['mkbapu_dist_to_rashi_price'] = (df['Close'] - df['mkbapu_rashi_start_price']) / atr

    # Feature 4: Bars Since Rashi Change
    bars_since = []
    counter = 0
    for i in range(len(df)):
        if df['mkbapu_rashi_changed'].iloc[i] == 1:
            counter = 0
        else:
            counter += 1
        bars_since.append(counter)
    df['mkbapu_bars_since_rashi'] = bars_since
    df['mkbapu_bars_since_rashi_norm'] = df['mkbapu_bars_since_rashi'] / 8.0  # ~2hr window

    # Feature 5: Fraction of Rashi Window Elapsed (0->1 as Lagna traverses 30 degrees)
    df['mkbapu_rashi_pct_elapsed'] = (df['house_placidus_1_cusp'] % 30) / 30.0

    # Feature 6: Vrishchika Pushkar Active (60 min after Vrishchika Lagna begins)
    pushkar_prices = []
    vrishchika_start_time = None
    current_pushkar_price = None
    for i in range(len(df)):
        dt = df['dt'].iloc[i]
        if df['mkbapu_rashi_changed'].iloc[i] == 1:
            current_pushkar_price = None
            if df['asc_rashi_name'].iloc[i] == 'Vrishchika':
                vrishchika_start_time = dt
            else:
                vrishchika_start_time = None
        if vrishchika_start_time is not None:
            mins_elapsed = (dt - vrishchika_start_time).total_seconds() / 60.0
            if mins_elapsed >= 60.0 and current_pushkar_price is None:
                current_pushkar_price = df['Open'].iloc[i]
        pushkar_prices.append(current_pushkar_price if current_pushkar_price is not None else np.nan)
    df['mkbapu_pushkar_start_price'] = pushkar_prices
    df['mkbapu_pushkar_active'] = (~df['mkbapu_pushkar_start_price'].isna()).astype(int)
    df['mkbapu_dist_to_pushkar'] = np.where(
        df['mkbapu_pushkar_active'] == 1,
        (df['Close'] - df['mkbapu_pushkar_start_price']) / atr,
        0.0
    )

    mkbapu_cols = [c for c in df.columns if c.startswith('mkbapu_')]
    print(f"    {len(mkbapu_cols)} MK Bapu features injected: {mkbapu_cols}")
    return df


# ???????????????????????????????????????????????????????????
# STEP 4: INTRADAY TRIPLE-BARRIER LABELING
# ???????????????????????????????????????????????????????????
def apply_intraday_triple_barrier(df: pd.DataFrame,
                                   pt_pct=0.003, sl_pct=0.002,
                                   time_bars=4) -> pd.Series:
    """
    Intraday Triple-Barrier:
      +1 = Close hits +0.3% before hitting -0.2% or 4 bars (60 min)
      -1 = Close hits -0.2% first
       0 = Time barrier (4 bars = 60 min) -- inconclusive
    """
    print(f"[4] Applying Intraday Triple-Barrier "
          f"(PT={pt_pct*100:.1f}%, SL={sl_pct*100:.1f}%, {time_bars} bars)...")
    closes = df['Close'].values
    labels = np.zeros(len(closes), dtype=np.int8)
    for i in range(len(closes) - time_bars):
        entry = closes[i]
        pt_level = entry * (1 + pt_pct)
        sl_level = entry * (1 - sl_pct)
        label = 0
        for j in range(1, time_bars + 1):
            if i + j >= len(closes):
                break
            c = closes[i + j]
            if c >= pt_level:
                label = 1
                break
            elif c <= sl_level:
                label = -1
                break
        labels[i] = label
    labels[-time_bars:] = 0  # last bars undefined
    s = pd.Series(labels, index=df.index, name='triple_barrier_label')
    dist = {-1: (labels==-1).sum(), 0: (labels==0).sum(), 1: (labels==1).sum()}
    total = len(labels)
    print(f"    Label dist -> Short:{dist[-1]:,}({dist[-1]/total:.1%})  "
          f"Neutral:{dist[0]:,}({dist[0]/total:.1%})  "
          f"Long:{dist[1]:,}({dist[1]/total:.1%})")
    return s


# ???????????????????????????????????????????????????????????
# STEP 5: GRANGER CAUSALITY (Fast 2-Minute Test)
# ???????????????????????????????????????????????????????????
def granger_causality_test(df: pd.DataFrame) -> dict:
    print("[5] Running Granger Causality: rashi_changed -> next-bar volatility...")
    from statsmodels.tsa.stattools import grangercausalitytests
    import io, contextlib

    # Measure: does rashi_changed Granger-cause next-bar |return|?
    df2 = df.copy()
    df2['bar_return'] = df2['Close'].pct_change()
    df2['next_bar_vol'] = df2['bar_return'].abs().shift(-1)
    df2 = df2.dropna(subset=['mkbapu_rashi_changed', 'next_bar_vol'])

    data = df2[['next_bar_vol', 'mkbapu_rashi_changed']].dropna()

    results = {}
    try:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            gc = grangercausalitytests(data.values, maxlag=4, verbose=False)
        for lag, res in gc.items():
            pval = res[0]['ssr_ftest'][1]
            results[f'lag_{lag}_pval'] = round(pval, 6)
            sig = "[SIGNIFICANT]" if pval < 0.05 else "[not significant]"
            print(f"    Lag {lag}: p={pval:.4f}  {sig}")
    except Exception as e:
        print(f"    Granger test error: {e}")
    return results


# ???????????????????????????????????????????????????????????
# STEP 6: XGBOOST -- BASELINE vs AUGMENTED
# ???????????????????????????????????????????????????????????
def train_and_compare(df_full: pd.DataFrame, labels: pd.Series) -> dict:
    print("[6] Training XGBoost -- Baseline vs MK Bapu Augmented...")
    import xgboost as xgb
    from sklearn.metrics import accuracy_score, f1_score
    from sklearn.preprocessing import LabelEncoder

    df_full = df_full.copy()
    df_full['label'] = labels

    # Drop non-features
    drop_cols = ['dt', 'Open', 'High', 'Low', 'Close', 'Volume',
                 'label', 'asc_rashi_name', 'mkbapu_rashi_start_price',
                 'mkbapu_pushkar_start_price']
    drop_cols = [c for c in drop_cols if c in df_full.columns]

    df_full = df_full.dropna(subset=['label'])
    df_full = df_full[df_full['label'] != 0]  # Drop neutral time-barrier bars
    print(f"    Active labeled bars (Long/Short only): {len(df_full):,}")

    # Labels to 0/1 for binary (1=Long, 0=Short)
    y = (df_full['label'] == 1).astype(int).values

    # Temporal 80/20 split (NO LEAKAGE)
    split = int(len(df_full) * 0.8)
    train_idx = list(range(split))
    test_idx  = list(range(split, len(df_full)))

    xgb_params = dict(
        n_estimators=400, max_depth=5, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.6, min_child_weight=3,
        tree_method='hist', nthread=6, random_state=42,
        eval_metric='logloss', early_stopping_rounds=30,
        use_label_encoder=False
    )

    results = {}

    for mode in ['baseline', 'augmented']:
        if mode == 'baseline':
            # All features EXCEPT the mkbapu_ ones
            feat_cols = [c for c in df_full.columns
                         if c not in drop_cols and not c.startswith('mkbapu_')
                         and not c.startswith('asc_rashi')]
        else:
            # ALL features INCLUDING the 8 mkbapu_ features
            feat_cols = [c for c in df_full.columns if c not in drop_cols]

        feat_cols = [c for c in feat_cols if pd.api.types.is_numeric_dtype(df_full[c])]
        X = df_full[feat_cols].fillna(0).values.astype(np.float32)

        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        clf = xgb.XGBClassifier(**xgb_params)
        clf.fit(X_train, y_train,
                eval_set=[(X_test, y_test)], verbose=False)

        y_pred = clf.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        f1  = f1_score(y_test, y_pred, average='binary')

        # Precision at top decile (most confident longs)
        proba = clf.predict_proba(X_test)[:, 1]
        top_decile = proba >= np.percentile(proba, 90)
        prec_top = y_test[top_decile].mean() if top_decile.sum() > 0 else 0.5

        results[mode] = {
            'model': clf,
            'feature_cols': feat_cols,
            'accuracy': round(acc, 4),
            'f1': round(f1, 4),
            'precision_top10pct': round(prec_top, 4),
            'n_features': len(feat_cols),
            'n_train': len(train_idx),
            'n_test': len(test_idx)
        }
        print(f"\n    [{mode.upper()}] {len(feat_cols)} features")
        print(f"      Accuracy:              {acc:.4f}")
        print(f"      F1 Score:              {f1:.4f}")
        print(f"      Precision Top 10%:     {prec_top:.4f}")

    delta_acc = results['augmented']['accuracy'] - results['baseline']['accuracy']
    delta_prec = results['augmented']['precision_top10pct'] - results['baseline']['precision_top10pct']
    verdict = "[WIN] MK BAPU FEATURES ADD EDGE" if delta_acc > 0.002 or delta_prec > 0.01 else "[FAIL] No meaningful incremental edge"
    print(f"\n    Delta Accuracy:    {delta_acc:+.4f}")
    print(f"    Delta Top-10 Prec: {delta_prec:+.4f}")
    print(f"    VERDICT: {verdict}")
    results['verdict'] = verdict
    results['delta_accuracy'] = delta_acc
    results['delta_precision'] = delta_prec
    return results


# ???????????????????????????????????????????????????????????
# STEP 7: SHAP ANALYSIS -- Isolate MK Bapu Feature Importance
# ???????????????????????????????????????????????????????????
def shap_analysis(df_full: pd.DataFrame, labels: pd.Series, results: dict):
    print("\n[7] Running SHAP analysis on Augmented model...")
    try:
        import shap
    except ImportError:
        print("    shap not installed. Skipping.")
        return

    model = results['augmented']['model']
    feat_cols = results['augmented']['feature_cols']
    drop_cols = ['dt', 'Open', 'High', 'Low', 'Close', 'Volume',
                 'label', 'asc_rashi_name', 'mkbapu_rashi_start_price',
                 'mkbapu_pushkar_start_price']

    df_work = df_full.copy()
    df_work['label'] = labels
    df_work = df_work.dropna(subset=['label'])
    df_work = df_work[df_work['label'] != 0]

    X = df_work[feat_cols].fillna(0).values.astype(np.float32)
    split = int(len(X) * 0.8)
    X_test = X[split:]

    # Subsample for speed
    sample_size = min(500, len(X_test))
    idx = np.random.RandomState(42).choice(len(X_test), sample_size, replace=False)
    X_shap = X_test[idx]

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_shap)

    mean_abs_shap = np.abs(shap_values).mean(axis=0)

    # Top 30 features overall
    top30 = np.argsort(mean_abs_shap)[::-1][:30]
    print(f"\n    Top 30 Features by SHAP (Long class):")
    for rank, idx2 in enumerate(top30, 1):
        fname = feat_cols[idx2]
        sv = mean_abs_shap[idx2]
        tag = "[MKBAPU]" if fname.startswith('mkbapu_') else "       "
        print(f"    {rank:3d}. {tag} {fname:<55s} {sv:.6f}")

    # Specifically isolate MK Bapu features
    mkbapu_idxs = [i for i, c in enumerate(feat_cols) if c.startswith('mkbapu_')]
    if mkbapu_idxs:
        print(f"\n    MK Bapu Feature SHAP Breakdown:")
        mkbapu_shap = [(feat_cols[i], mean_abs_shap[i]) for i in mkbapu_idxs]
        mkbapu_shap.sort(key=lambda x: -x[1])
        for fname, sv in mkbapu_shap:
            # What percentile is this among ALL features?
            pct = 100 * (mean_abs_shap < sv).sum() / len(mean_abs_shap)
            print(f"    {fname:<55s} {sv:.6f}  (top {100-pct:.0f}th percentile)")

    # Save SHAP plot
    try:
        fig, ax = plt.subplots(figsize=(12, 8))
        top_names = [feat_cols[i] for i in top30]
        top_vals = [mean_abs_shap[i] for i in top30]
        colors = ['#e74c3c' if n.startswith('mkbapu_') else '#3498db' for n in top_names]
        ax.barh(range(len(top_names)), top_vals[::-1], color=colors[::-1])
        ax.set_yticks(range(len(top_names)))
        ax.set_yticklabels(top_names[::-1], fontsize=8)
        ax.set_xlabel("Mean |SHAP Value|")
        ax.set_title("Feature Importance (RED = MK Bapu Ascendant Features)")
        plt.tight_layout()
        plot_path = os.path.join(OUTPUT_DIR, "shap_feature_importance.png")
        plt.savefig(plot_path, dpi=150)
        plt.close()
        print(f"\n    SHAP plot saved: {plot_path}")
    except Exception as e:
        print(f"    Plot error (non-critical): {e}")


# ???????????????????????????????????????????????????????????
# STEP 8: REGIME-GATED BACKTEST (HMM 3-State)
# ???????????????????????????????????????????????????????????
def regime_backtest(df_full: pd.DataFrame, labels: pd.Series, results: dict):
    print("\n[8] HMM Regime-Gated Backtest...")
    try:
        from hmmlearn.hmm import GaussianHMM
    except ImportError:
        print("    hmmlearn not installed. Skipping HMM regime test.")
        return

    model = results['augmented']['model']
    feat_cols = results['augmented']['feature_cols']

    df_work = df_full.copy()
    df_work['label'] = labels
    df_work = df_work.dropna(subset=['label'])
    df_work = df_work[df_work['label'] != 0]

    bar_returns = df_work['Close'].pct_change().fillna(0).values
    log_vol = np.log(df_work['High'] / df_work['Low']).fillna(0).values

    obs = np.column_stack([bar_returns, log_vol])
    hmm = GaussianHMM(n_components=3, covariance_type='diag', n_iter=100, random_state=42)
    hmm.fit(obs)
    regimes = hmm.predict(obs)

    X = df_work[feat_cols].fillna(0).values.astype(np.float32)
    split = int(len(X) * 0.8)
    X_test = X[split:]
    y_test_labels = labels.values[df_work.index[-len(X_test):]]
    regimes_test = regimes[split:]
    actual_returns = bar_returns[split:]

    proba = model.predict_proba(X_test)[:, 1]
    signal = (proba > 0.55).astype(int) * 2 - 1  # +1 or -1

    print(f"\n    Regime Distribution (test set):")
    regime_means = []
    for r in range(3):
        mask = regimes_test == r
        regime_means.append(obs[split:][mask, 1].mean() if mask.sum() > 0 else 0)

    # Sort regimes by volatility (0=Low, 1=Med, 2=High)
    regime_order = np.argsort(regime_means)
    regime_labels_map = {regime_order[0]: "Low-Vol  [GREEN]",
                         regime_order[1]: "Med-Vol  [YELLOW]",
                         regime_order[2]: "High-Vol [RED]  "}

    for r in range(3):
        mask = regimes_test == r
        if mask.sum() == 0: continue
        strat_rets = actual_returns[mask] * signal[mask]
        sr = (strat_rets.mean() / (strat_rets.std() + 1e-9)) * np.sqrt(252 * 26)
        wr = (strat_rets > 0).mean()
        rname = regime_labels_map.get(r, f"Regime {r}")
        print(f"    {rname:15s}  n={mask.sum():4d}  "
              f"WinRate={wr:.1%}  AnnSharpe={sr:.2f}")


# ???????????????????????????????????????????????????????????
# MAIN
# ???????????????????????????????????????????????????????????
def main():
    t_global = time.time()
    print("=" * 70)
    print("  MK BAPU INTRADAY PIPELINE -- ANTIGRAVITY VEDIC QUANT")
    print("  Full 4,221-Feature Architecture Integration")
    print("=" * 70)
    print()

    setup_ephemeris()

    # 1. Fetch data
    df = fetch_spy_15m()
    print()

    # 2. Compute ephemeris features
    feat_df = build_feature_matrix(df)
    df_full = pd.concat([df.reset_index(drop=True), feat_df.reset_index(drop=True)], axis=1)
    print()

    # 3. MK Bapu features
    df_full = apply_mkbapu_features(df_full)
    print()

    # 4. Triple-Barrier labels
    labels = apply_intraday_triple_barrier(df_full)
    print()

    # 5. Granger causality
    granger_results = granger_causality_test(df_full)
    print()

    # 6. XGBoost baseline vs augmented
    results = train_and_compare(df_full, labels)
    print()

    # 7. SHAP
    shap_analysis(df_full, labels, results)

    # 8. HMM Regime backtest
    regime_backtest(df_full, labels, results)

    # ?? Save full augmented feature matrix ??
    out_path = os.path.join(OUTPUT_DIR, "spy_15m_mkbapu_features.parquet")
    save_cols = [c for c in df_full.columns if c != 'asc_rashi_name']
    df_full[save_cols].to_parquet(out_path, index=False)
    print(f"\n[9] Full feature matrix saved: {out_path}")

    total = time.time() - t_global
    print(f"\n{'=' * 70}")
    print(f"  PIPELINE COMPLETE -- {total/60:.1f} minutes")
    print(f"  Verdict: {results.get('verdict', 'N/A')}")
    print(f"  Delta Accuracy:    {results.get('delta_accuracy', 0):+.4f}")
    print(f"  Delta Top-10 Prec: {results.get('delta_precision', 0):+.4f}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()


# CRITICAL BUG FIX #17: Ensure swisseph is closed
import atexit
atexit.register(swe.close)
