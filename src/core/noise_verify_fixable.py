"""
PHASE 2: NOISE VERIFICATION of forensics-discovered FIXABLE assets.
We cannot trust ANY of the new high-CAGR numbers until they pass the noise gate.
This script re-runs each FIXABLE asset at its OPTIMAL BARRIER with:
  A) Real planetary features
  B) Gaussian random noise features (same shape)
And computes the Real-Noise delta. Only positive deltas are genuinely fixed.

CRITICAL SUSPECTED OVERFIT: GLD +3399%, SLV +1851% at 24h barrier.
These MUST be challenged with the noise test immediately.
"""
import os, numpy as np, pandas as pd, yfinance as yf, xgboost as xgb, warnings
warnings.filterwarnings("ignore")
from sklearn.model_selection import TimeSeriesSplit

BASE_DIR   = r"C:\Users\patel\Desktop\Python\Learn"
MATRIX_FILE = os.path.join(BASE_DIR, "genesis_9000_MUNDANE.parquet")

# Assets + their forensics-discovered optimal barriers
FIXABLE = {
    # asset: (ticker, bench, optimal_barrier, planet_feats_found, use_planet_spec)
    "GLD":  ("GLD",  "SPY", 24, True),   # +3399% — SUSPECT. Need noise gate.
    "SLV":  ("SLV",  "SPY", 24, False),  # +1851% — SUSPECT. Need noise gate.
    "NLR":  ("NLR",  "SPY", 24, False),  # +270%  — need noise gate
    "GDX":  ("GDX",  "SPY", 12, True),   # +250% spec — EXCITING. Need noise gate.
    "XME":  ("XME",  "SPY", 12, False),  # +200% — need noise gate
    "JETS": ("JETS", "SPY", 24, False),  # +170% — was WORST noise failure before. TEST.
    "XBI":  ("XBI",  "SPY", 12, False),  # +62%  — need noise gate
    "XLC":  ("XLC",  "SPY", 12, False),  # +53%  — need noise gate
    "XLK":  ("XLK",  "SPY",  6, False),  # +40%  — need noise gate
    "XLE":  ("XLE",  "SPY", 12, False),  # +30%  — need noise gate
    "XOP":  ("XOP",  "SPY", 24, False),  # +27%  — need noise gate
    "PAVE": ("PAVE", "SPY",  3, False),  # +10%  — need noise gate
    # Marginal — test too
    "URA":  ("URA",  "SPY",  3, False),  # +9.5%
    "HACK": ("HACK", "SPY",  6, False),  # +7.8%
    "XLI":  ("XLI",  "SPY",  3, False),  # +5.3%
}

# Planet-specific feature logic — only for assets where we found >0 planet features
RULERSHIPS = {
    "GLD": ["Sun", "Venus", "Jupiter"],
    "GDX": ["Sun", "Venus", "Saturn"],
    "TAN": ["Sun", "Uranus"],
    "XLY": ["Venus", "Sun"],
}

def get_planet_cols(rulers, all_cols):
    return [c for c in all_cols
            if any(p.upper() in c.upper() for p in rulers)]

print("="*90)
print(" NOISE VERIFICATION: Forensics-Discovered FIXABLE Assets")
print(" Rule: Real CAGR > Noise CAGR = genuine signal. Fail = still overfit.")
print("="*90)

# Load matrix once
df_astro = pd.read_parquet(MATRIX_FILE)
df_astro["Date"] = pd.to_datetime(df_astro["Date"]).dt.tz_localize(None).astype("datetime64[us]")
for c in ["Close","Volume"]:
    if c in df_astro.columns: df_astro.drop(columns=[c], inplace=True)

all_astro_cols = df_astro.columns.tolist()

results = {}
for asset_name, (ticker, bench, BARRIER, use_spec) in FIXABLE.items():
    print(f"\n--- {asset_name} | Barrier={BARRIER}h ---")
    try:
        df_a = yf.download(ticker, period="730d", interval="1h", progress=False, auto_adjust=False)
        df_b = yf.download(bench,  period="730d", interval="1h", progress=False, auto_adjust=False)
    except Exception as e:
        print(f"  Download failed: {e}"); continue
    if df_a.empty or df_b.empty: continue
    if isinstance(df_a.columns, pd.MultiIndex): df_a.columns = df_a.columns.get_level_values(0)
    if isinstance(df_b.columns, pd.MultiIndex): df_b.columns = df_b.columns.get_level_values(0)
    df_a = df_a[["Close","Volume"]].dropna()
    df_b = df_b[["Close"]].dropna()
    da, db = df_a.align(df_b, join="inner", axis=0)
    syn = pd.DataFrame()
    syn["Close"]  = da["Close"] / db["Close"]
    syn["Volume"] = da["Volume"]
    syn["dt"]     = syn.index
    mask = (syn.index.hour >= 9) & (syn.index.hour <= 15)
    syn = syn[mask].reset_index(drop=True)
    syn["Date"] = pd.to_datetime(syn["dt"]).dt.tz_localize(None).astype("datetime64[us]")

    fused = pd.merge_asof(syn.sort_values("Date"), df_astro.sort_values("Date"),
                          on="Date", direction="backward")
    fused = fused.dropna(subset=["Tithi_Num"]).reset_index(drop=True)
    closes = fused["Close"].values
    n = len(closes)

    exclude = {"Close","Volume","dt","Date","index","label"}
    all_feat_cols = [c for c in fused.columns if c not in exclude and
                     fused[c].dtype in [np.float32, np.float64, np.int64, np.int32, int, float]]

    # Feature set: planet-specific if available, else all
    if use_spec and asset_name in RULERSHIPS:
        rulers = RULERSHIPS[asset_name]
        spec_cols = get_planet_cols(rulers, all_feat_cols)
        if len(spec_cols) >= 20:
            feat_cols = spec_cols
            print(f"  Using {len(feat_cols)} planet-specific features ({rulers})")
        else:
            feat_cols = all_feat_cols
            print(f"  Planet features insufficient ({len(spec_cols)}), using all {len(all_feat_cols)}")
    else:
        feat_cols = all_feat_cols
        print(f"  Using all {len(all_feat_cols)} features")

    # Labels
    labels = np.zeros(n, dtype=np.int8)
    for i in range(n - BARRIER):
        labels[i] = 1 if closes[i + BARRIER] > closes[i] else 0
    df2 = fused.copy()
    df2["label"] = labels
    df2 = df2.iloc[:-BARRIER].reset_index(drop=True)
    n2 = len(df2)

    X_real  = df2[feat_cols].fillna(0).values.astype(np.float32)
    # Noise: same shape, pure Gaussian (same mean/std per column to avoid scaling issues)
    rng     = np.random.RandomState(42)
    X_noise = rng.randn(*X_real.shape).astype(np.float32)
    y       = df2["label"].values

    tscv = TimeSeriesSplit(n_splits=5)
    xp   = dict(n_estimators=30, max_depth=3, learning_rate=0.05,
                tree_method="hist", random_state=42,
                reg_alpha=1.5, reg_lambda=1.5)

    real_rets, noise_rets = [], []
    for tr, te in tscv.split(X_real):
        clean_tr = tr[:-BARRIER] if len(tr) > BARRIER else tr
        if len(clean_tr) < 50 or len(np.unique(y[clean_tr])) < 2: continue
        # Real
        mr = xgb.XGBClassifier(**xp)
        mr.fit(X_real[clean_tr], y[clean_tr], verbose=False)
        pr = mr.predict(X_real[te])
        # Noise
        mn = xgb.XGBClassifier(**xp)
        mn.fit(X_noise[clean_tr], y[clean_tr], verbose=False)
        pn = mn.predict(X_noise[te])
        for i, idx in enumerate(te):
            if idx >= n2 - BARRIER: continue
            move = (closes[idx + BARRIER] / closes[idx]) - 1.0
            if pr[i] == 1: real_rets.append(move)
            if pn[i] == 1: noise_rets.append(move)

    def cagr(rets, years=2.9):
        if not rets: return -99.0
        eq = np.cumprod(1 + np.array(rets))
        return round((eq[-1]**(1/years) - 1)*100, 1)

    real_cagr  = cagr(real_rets)
    noise_cagr = cagr(noise_rets)
    delta      = real_cagr - noise_cagr
    noise_pass = delta > 0
    real_wr    = round((np.array(real_rets) > 0).mean()*100, 1) if real_rets else 0

    results[asset_name] = {
        "barrier": BARRIER, "real_cagr": real_cagr,
        "noise_cagr": noise_cagr, "delta": delta,
        "noise_pass": noise_pass, "wr": real_wr,
        "n_trades": len(real_rets)
    }
    flag = "PASS" if noise_pass else "FAIL"
    print(f"  [{flag}] Real={real_cagr:+.1f}%  Noise={noise_cagr:+.1f}%  "
          f"Delta={delta:+.1f}%  WR={real_wr}%  Trades={len(real_rets)}")

print("\n" + "="*90)
print(" FINAL NOISE GATE RESULTS: New Optimal-Barrier Assets")
print("="*90)
print(f"{'ASSET':<6}  {'BARRIER':>7}  {'REAL CAGR':>10}  {'NOISE CAGR':>11}  "
      f"{'DELTA':>8}  {'WR':>6}  {'NOISE GATE':>11}  {'VERDICT':>12}")
print("-"*90)
passed = []
for asset, r in sorted(results.items(), key=lambda x: -x[1]["real_cagr"]):
    flag = "PASS ✅" if r["noise_pass"] else "FAIL ❌"
    verdict = "NEW TRADE" if r["noise_pass"] and r["real_cagr"] > 10 else \
              ("BORDERLINE" if r["noise_pass"] else "STILL NOISE")
    print(f"{asset:<6}  {r['barrier']:>6}h  {r['real_cagr']:>+9.1f}%  "
          f"{r['noise_cagr']:>+10.1f}%  {r['delta']:>+7.1f}%  "
          f"{r['wr']:>5.1f}%  {flag:>11}  {verdict:>12}")
    if r["noise_pass"] and r["real_cagr"] > 10:
        passed.append((asset, r))

print(f"\nNoise gate passed with positive CAGR: {len(passed)} new assets eligible for live trading")
for asset, r in sorted(passed, key=lambda x: -x[1]["real_cagr"]):
    print(f"  -> {asset:<6} @ {r['barrier']}h barrier | CAGR={r['real_cagr']:+.1f}% | "
          f"Noise Delta={r['delta']:+.1f}%")
