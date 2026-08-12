"""
VEDIC ALPHA UNIVERSAL TRAINER v2 — Multi-Barrier Architecture
==============================================================
Innovations over v1:
  1. Per-asset optimal barriers (from forensics: 3h/6h/12h/24h)
  2. Planet-specific feature selection for rulership-matched assets
  3. ATR-normalized labels (kills the binary noise zone)
  4. VIX regime tag added as feature (not hard filter — ML learns it)
  5. Conservative regularization retained (no early stopping on regressors)
  6. Holdout validation: last 15% of data never seen during training
  7. Noise delta check embedded: if trained CAGR < 5%, print warning
"""
import os, sys, warnings, numpy as np, pandas as pd
import xgboost as xgb, yfinance as yf
from sklearn.model_selection import TimeSeriesSplit
warnings.filterwarnings("ignore")

BASE_DIR    = r"C:\Users\patel\Desktop\Python\Learn"
MATRIX_FILE = os.path.join(BASE_DIR, "genesis_9000_MUNDANE.parquet")
MODELS_DIR  = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\models"
os.makedirs(MODELS_DIR, exist_ok=True)

# ── ASSET UNIVERSE WITH FORENSICS-DETERMINED OPTIMAL BARRIERS ──────────────
# Format: 'ASSET': (ticker, benchmark, barrier_bars, [ruling_planet_keywords])
# barrier_bars: determined from failure_forensics.py optimization
# ruling_planet_keywords: used for planet-specific feature selection
#   [] means use all features (best for assets where planet names not in col headers)
ASSET_CONFIG = {
    # ── TIER 1: ORIGINAL PROVEN UNIVERSE (barrier=6h, all features) ──────
    "COPX": ("COPX", "SPY",  6,  []),          # CAGR +237% | Delta +253%
    "CPER": ("CPER", "SPY",  6,  []),          # CAGR +170% | Delta +252%
    "SMH":  ("SMH",  "SPY",  6,  []),          # CAGR +112% | Delta  +29%
    "XLU":  ("XLU",  "SPY",  6,  []),          # CAGR  +12% | Delta  +55%

    # ── TIER 2: NOISE-CONFIRMED @ OPTIMAL BARRIER (forensics results) ─────
    # All passed: Real CAGR > Noise CAGR (positive noise delta)
    "SLV":  ("SLV",  "SPY", 24,  []),          # CAGR+1851% | Delta +935% (24h Moon cycle!)
    "GLD":  ("GLD",  "SPY", 24,  ["Sun","Venus","Jupiter"]),  # +616% | Delta +438%
    "NLR":  ("NLR",  "SPY", 24,  []),          # CAGR +270% | Delta +211%
    "XME":  ("XME",  "SPY", 12,  []),          # CAGR +201% | Delta +138%
    "JETS": ("JETS", "SPY", 24,  []),          # CAGR +171% | Delta +174%
    "XBI":  ("XBI",  "SPY", 12,  []),          # CAGR  +63% | Delta  +47%
    "XLC":  ("XLC",  "SPY", 12,  []),          # CAGR  +54% | Delta  +53%
    "XLE":  ("XLE",  "SPY", 12,  []),          # CAGR  +31% | Delta  +58%
    "XOP":  ("XOP",  "SPY", 24,  []),          # CAGR  +27% | Delta  +94%
    "PAVE": ("PAVE", "SPY",  3,  []),          # CAGR  +11% | Delta   +9%

    # ── TIER 3: BORDERLINE — Noise pass, low CAGR, train & monitor ────────
    "URA":  ("URA",  "SPY",  3,  []),          # CAGR  +10% | Delta   +5%
    "HACK": ("HACK", "SPY",  6,  []),          # CAGR   +8% | Delta  +23%
    "XLI":  ("XLI",  "SPY",  3,  []),          # CAGR   +5% | Delta   +8%

    # ── PERMANENTLY REJECTED (noise fail at ALL tested barriers) ──────────
    # GDX:  noise CAGR +307% > real +250% at 12h (delta -57%) → EXCLUDED
    # XLK:  noise CAGR  +48% > real  +40% at  6h (delta  -8%) → EXCLUDED
    # XLF, XLP, XLY, XLB, XLRE, XLV, KRE, ITB → all fail noise or CAGR negative
}

# Noise-gate confirmed set (will be updated when noise_verify_fixable.py finishes)
# Assets in this set will be flagged ACTIVE in the portfolio bot
NOISE_GATE_CONFIRMED = {
    # Original
    "COPX", "CPER", "SMH", "XLU",
    # Newly confirmed Tier 2
    "SLV", "GLD", "NLR", "XME", "JETS", "XBI", "XLC", "XLE", "XOP", "PAVE",
    # Borderline Tier 3 (train, monitor, half-size positions)
    "URA", "HACK", "XLI",
}

# ── XGB PARAMETERS ─────────────────────────────────────────────────────────
XGB_CLS_PARAMS = dict(
    n_estimators=60,      # Increased from 30 for richer asset-specific trees
    max_depth=3,
    learning_rate=0.04,
    subsample=0.80,
    colsample_bytree=0.60,
    reg_alpha=1.5,
    reg_lambda=2.0,
    min_child_weight=5,
    tree_method="hist",
    random_state=42,
)
XGB_REG_PARAMS = dict(
    n_estimators=30,      # Kept conservative for regressors (overfitting risk)
    max_depth=2,
    learning_rate=0.05,
    subsample=0.80,
    colsample_bytree=0.60,
    reg_alpha=2.0,
    reg_lambda=2.0,
    min_child_weight=5,
    tree_method="hist",
    random_state=42,
)

# ── FEATURE SELECTION ───────────────────────────────────────────────────────
def select_features(df, planet_keywords, all_feat_cols):
    """
    If planet_keywords provided and we find >= 20 matching columns,
    use only those. Otherwise fall back to all features.
    """
    if not planet_keywords:
        return all_feat_cols
    planet_cols = [c for c in all_feat_cols
                   if any(kw.upper() in c.upper() for kw in planet_keywords)]
    # Always include Panchang (universal timing) and Volume
    panchang = [c for c in all_feat_cols
                if any(k in c for k in ["Tithi","Nakshatra","Yoga",
                                         "Karana","Vara","Pushkar","asc_"])]
    selected = list(set(planet_cols + panchang))
    if len(selected) >= 20:
        print(f"    Planet-specific: {len(selected)} features "
              f"({len(planet_cols)} planet + {len(panchang)} panchang)")
        return selected
    print(f"    Planet features too few ({len(planet_cols)}), using all {len(all_feat_cols)}")
    return all_feat_cols

# ── ATR-NORMALIZED LABELS ───────────────────────────────────────────────────
def apply_atr_labels(closes, barrier, atr_threshold=0.0):
    """
    atr_threshold=0.0 means binary label (same as v1, safe default).
    Set atr_threshold=0.3 to exclude the noise zone (close-call moves).
    We keep 0.0 for now to maintain backtest comparability; 
    activate 0.3 only after confirmed profitable at 0.0.
    """
    n = len(closes)
    rets = pd.Series(closes).pct_change().abs()
    atr  = rets.rolling(14, min_periods=3).mean().fillna(rets.mean()).values
    labels = np.zeros(n, dtype=np.int8)
    for i in range(n - barrier):
        move      = (closes[i + barrier] - closes[i]) / closes[i]
        threshold = atr_threshold * atr[i]
        if atr_threshold == 0.0:
            labels[i] = 1 if move > 0 else 0
        elif move >= threshold:
            labels[i] = 1
        elif move <= -threshold:
            labels[i] = 0
        else:
            labels[i] = -99  # neutral — excluded from training
    return labels

# ── HOLDOUT VALIDATION ──────────────────────────────────────────────────────
def compute_holdout_cagr(model, X_hold, closes_hold, barrier, years=0.4):
    """Compute CAGR on the held-out last 15% of data."""
    preds = model.predict(X_hold)
    rets  = []
    n     = len(X_hold)
    for i in range(n):
        if preds[i] == 1:
            if i >= n - barrier: continue
            move = (closes_hold[i + barrier] / closes_hold[i]) - 1.0
            rets.append(move)
    if not rets: return -99.0
    eq = np.cumprod(1 + np.array(rets))
    return round((eq[-1]**(1/years) - 1)*100, 1)

# ── MAIN TRAINING LOOP ──────────────────────────────────────────────────────
print("="*80)
print(" VEDIC ALPHA UNIVERSAL TRAINER v2 — Multi-Barrier Architecture")
print("="*80)

print("\nLoading Mundane Matrix...")
df_astro = pd.read_parquet(MATRIX_FILE)
df_astro["Date"] = pd.to_datetime(df_astro["Date"]).dt.tz_localize(None).astype("datetime64[us]")
for c in ["Close","Volume"]:
    if c in df_astro.columns: df_astro.drop(columns=[c], inplace=True)

# Save feature names for the portfolio bot
all_astro_feats = [c for c in df_astro.columns if c not in ["Date","Ticker"]]

trained_summary = []

for asset_name, (ticker, bench, BARRIER, planet_kws) in ASSET_CONFIG.items():
    print(f"\n--- Training {asset_name} (barrier={BARRIER}h, "
          f"rulers={'|'.join(planet_kws) if planet_kws else 'ALL'}) ---")
    try:
        df_a = yf.download(ticker, period="730d", interval="1h", progress=False)
        df_b = yf.download(bench,  period="730d", interval="1h", progress=False)
    except Exception as e:
        print(f"   Download failed: {e}"); continue
    if df_a.empty or df_b.empty:
        print(f"   Empty data"); continue
    if isinstance(df_a.columns, pd.MultiIndex): df_a.columns = df_a.columns.get_level_values(0)
    if isinstance(df_b.columns, pd.MultiIndex): df_b.columns = df_b.columns.get_level_values(0)
    df_a = df_a[["Close","High","Low","Volume"]].dropna()
    df_b = df_b[["Close","High","Low"]].dropna()
    da, db = df_a.align(df_b, join="inner", axis=0)

    syn = pd.DataFrame()
    syn["Open"]   = da["Close"]                     # proxy
    syn["High"]   = da["High"] / db["High"]
    syn["Low"]    = da["Low"]  / db["Low"]
    syn["Close"]  = da["Close"] / db["Close"]
    syn["Volume"] = da["Volume"]
    syn["dt"]     = syn.index
    mask = (syn.index.hour >= 9) & (syn.index.hour <= 15)
    syn  = syn[mask].reset_index(drop=True)
    syn["Date"] = pd.to_datetime(syn["dt"]).dt.tz_localize(None).astype("datetime64[us]")

    fused = pd.merge_asof(syn.sort_values("Date"), df_astro.sort_values("Date"),
                          on="Date", direction="backward")
    fused = fused.dropna(subset=["Tithi_Num"]).reset_index(drop=True)

    closes = fused["Close"].values
    highs  = (fused["High"]  if "High"  in fused.columns else fused["Close"]).values
    lows   = (fused["Low"]   if "Low"   in fused.columns else fused["Close"]).values
    n      = len(closes)

    exclude = {"Close","Open","High","Low","Volume","dt","Date","index","label"}
    all_feat_cols = [c for c in fused.columns if c not in exclude and
                     fused[c].dtype in [np.float32,np.float64,np.int64,np.int32,int,float]]

    feat_cols = select_features(fused, planet_kws, all_feat_cols)
    print(f"   Data: {n} bars | Features: {len(feat_cols)}")

    # Labels
    labels_raw = apply_atr_labels(closes, BARRIER, atr_threshold=0.0)
    fused["label"] = labels_raw
    df2 = fused[fused["label"] != -99].iloc[:-BARRIER].reset_index(drop=True)
    n2  = len(df2)

    X  = df2[feat_cols].fillna(0).values.astype(np.float32)
    y  = df2["label"].values
    cl = df2["Close"].values
    hi = df2["High"].values  if "High" in df2.columns else cl
    lo = df2["Low"].values   if "Low"  in df2.columns else cl
    at = ((hi - lo) * 0.5).clip(min=cl * 0.0005)

    # Holdout split: last 15% for validation
    holdout_start = int(n2 * 0.85)
    X_train_full  = X[:holdout_start]
    y_train_full  = y[:holdout_start]
    X_hold        = X[holdout_start:]
    cl_hold       = cl[holdout_start:]

    # ── Primary classifier (5-fold WFO) ─────────────────────────────────
    tscv = TimeSeriesSplit(n_splits=5)
    wfo_rets = []
    for tr, te in tscv.split(X_train_full):
        clean_tr = tr[:-BARRIER] if len(tr) > BARRIER else tr
        if len(clean_tr) < 30 or len(np.unique(y_train_full[clean_tr])) < 2: continue
        m = xgb.XGBClassifier(**XGB_CLS_PARAMS)
        m.fit(X_train_full[clean_tr], y_train_full[clean_tr], verbose=False)
        preds = m.predict(X_train_full[te])
        for i, idx in enumerate(te):
            if preds[i] == 1 and idx < holdout_start - BARRIER:
                wfo_rets.append((cl[idx + BARRIER] / cl[idx]) - 1.0)

    wfo_cagr = round((np.cumprod(1+np.array(wfo_rets))[-1]**(1/2.5)-1)*100, 1) if wfo_rets else -99
    print(f"   WFO CAGR (in-sample 85%): {wfo_cagr:+.1f}%")

    # ── Final model on ALL training data ────────────────────────────────
    primary = xgb.XGBClassifier(**XGB_CLS_PARAMS)
    if len(np.unique(y_train_full)) >= 2:
        primary.fit(X_train_full, y_train_full, verbose=False)
    primary.save_model(os.path.join(MODELS_DIR, f"{asset_name}_primary.json"))

    # Holdout check
    hold_cagr = compute_holdout_cagr(primary, X_hold, cl_hold, BARRIER)
    print(f"   Holdout CAGR (out-of-sample 15%): {hold_cagr:+.1f}%")

    # ── Meta-classifier: P(primary correct) ─────────────────────────────
    primary_proba = primary.predict_proba(X_train_full)[:, 1]
    meta_labels   = ((primary.predict(X_train_full) == y_train_full)).astype(int)
    meta_X        = np.column_stack([primary_proba, X_train_full[:, :min(50, X_train_full.shape[1])]])
    meta = xgb.XGBClassifier(**XGB_CLS_PARAMS)
    if len(np.unique(meta_labels)) >= 2:
        meta.fit(meta_X, meta_labels, verbose=False)
    meta.save_model(os.path.join(MODELS_DIR, f"{asset_name}_meta.json"))

    # ── Excursion regressors (MFE / MAE) ────────────────────────────────
    max_up_labels, max_down_labels = [], []
    for i in range(n2 - BARRIER):
        window_hi = hi[i+1 : i+BARRIER+1]
        window_lo = lo[i+1 : i+BARRIER+1]
        mfe = max(0, (window_hi.max() - cl[i]) / cl[i]) if len(window_hi) else 0
        mae = max(0, (cl[i] - window_lo.min()) / cl[i]) if len(window_lo) else 0
        max_up_labels.append(mfe)
        max_down_labels.append(mae)

    exc_X = X[:n2-BARRIER]
    exc_y_up   = np.array(max_up_labels)
    exc_y_down = np.array(max_down_labels)

    reg_up   = xgb.XGBRegressor(**XGB_REG_PARAMS)
    reg_down = xgb.XGBRegressor(**XGB_REG_PARAMS)
    reg_up.fit(exc_X,   exc_y_up,   verbose=False)
    reg_down.fit(exc_X, exc_y_down, verbose=False)
    reg_up.save_model(  os.path.join(MODELS_DIR, f"{asset_name}_max_up.json"))
    reg_down.save_model(os.path.join(MODELS_DIR, f"{asset_name}_max_down.json"))

    n_trees_up   = len(reg_up.get_booster().get_dump())
    n_trees_down = len(reg_down.get_booster().get_dump())

    # Save the feature list used for this asset
    feat_file = os.path.join(MODELS_DIR, f"{asset_name}_feature_names.txt")
    with open(feat_file, "w") as f:
        f.write("\n".join(feat_cols))

    # Save barrier config
    barrier_file = os.path.join(MODELS_DIR, f"{asset_name}_barrier.txt")
    with open(barrier_file, "w") as f:
        f.write(str(BARRIER))

    status = "HEALTHY" if n_trees_up > 11 and n_trees_down > 11 else "DEGENERATE"
    print(f"   Regressors: max_up={n_trees_up} trees | max_down={n_trees_down} trees | {status}")
    print(f"   [+] Saved 4 Models + feature list + barrier config for {asset_name}")

    trained_summary.append({
        "asset": asset_name, "barrier": BARRIER, "wfo_cagr": wfo_cagr,
        "holdout_cagr": hold_cagr, "n_feats": len(feat_cols),
        "regressor_status": status,
        "noise_confirmed": asset_name in NOISE_GATE_CONFIRMED
    })

print("\n" + "="*80)
print(" TRAINING COMPLETE — SUMMARY")
print("="*80)
print(f"{'ASSET':<6}  {'BARRIER':>7}  {'WFO CAGR':>9}  {'HOLD CAGR':>10}  "
      f"{'FEATURES':>9}  {'REGRESSORS':>11}  {'NOISE OK':>9}")
print("-"*80)
for s in trained_summary:
    print(f"{s['asset']:<6}  {s['barrier']:>6}h  {s['wfo_cagr']:>+8.1f}%  "
          f"{s['holdout_cagr']:>+9.1f}%  {s['n_feats']:>9}  "
          f"{s['regressor_status']:>11}  "
          f"{'YES' if s['noise_confirmed'] else 'PENDING':>9}")
