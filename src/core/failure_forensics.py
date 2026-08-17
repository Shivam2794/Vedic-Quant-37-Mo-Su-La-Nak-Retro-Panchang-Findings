"""
FAILURE FORENSICS: Why did each rejected asset fail?
Diagnose root cause per asset across 4 failure modes:
 A. Slippage sensitivity (raw >> slip = liquidity issue)
 B. Noise failure (noise > real = price-structure overfitting)
 C. Barrier mismatch (6h wrong for the asset's volatility regime)
 D. Feature mismatch (generic 1704 features, no asset-specific planet weights)
"""
import os, numpy as np, pandas as pd, yfinance as yf, warnings
from sklearn.model_selection import TimeSeriesSplit
import xgboost as xgb
warnings.filterwarnings("ignore")

BASE_DIR   = r"C:\Users\patel\Desktop\Python\Learn"
MATRIX_FILE = os.path.join(BASE_DIR, "genesis_9000_MUNDANE.parquet")
BARRIER_OPTIONS = [3, 6, 12, 24]  # hours to test

ASSETS = {
    # Rejected noise-gate or losing, grouped by failure pattern
    "GLD":  ("GLD",  "SPY"),
    "SLV":  ("SLV",  "SPY"),
    "GDX":  ("GDX",  "SPY"),
    "URA":  ("URA",  "SPY"),
    "NLR":  ("NLR",  "SPY"),
    "XLE":  ("XLE",  "SPY"),
    "XLF":  ("XLF",  "SPY"),
    "XLI":  ("XLI",  "SPY"),
    "XLC":  ("XLC",  "SPY"),
    "XLK":  ("XLK",  "SPY"),
    "XLP":  ("XLP",  "SPY"),
    "XLRE": ("XLRE", "SPY"),
    "XLB":  ("XLB",  "SPY"),
    "XLY":  ("XLY",  "SPY"),
    "XLV":  ("XLV",  "SPY"),
    "KRE":  ("KRE",  "SPY"),
    "XBI":  ("XBI",  "SPY"),
    "JETS": ("JETS", "SPY"),
    "ITB":  ("ITB",  "SPY"),
    "HACK": ("HACK", "SPY"),
    "TAN":  ("TAN",  "SPY"),
    "PAVE": ("PAVE", "SPY"),
    "XME":  ("XME",  "SPY"),
    "XOP":  ("XOP",  "SPY"),
}

# VEDIC PLANETARY RULERSHIPS (classical + mundane astrology)
RULERSHIPS = {
    "GLD":  ["Sun", "Venus", "Jupiter"],          # Gold: Sun-ruled (Leo treasury)
    "SLV":  ["Moon"],                              # Silver: Moon-ruled classically
    "GDX":  ["Sun", "Venus", "Saturn"],            # Gold miners: Sun + Saturn (mining)
    "URA":  ["Uranus", "Saturn"],                  # Uranium: Uranus (nuclear), Saturn (mining)
    "NLR":  ["Uranus", "Saturn", "Jupiter"],       # Nuclear energy
    "XLE":  ["Neptune", "Jupiter", "Mars"],        # Oil/Energy: Neptune (gas/oil)
    "XLF":  ["Jupiter", "Venus", "Mercury"],       # Finance: Jupiter (wealth, expansion)
    "XLI":  ["Saturn", "Mars"],                    # Industrials: Saturn+Mars (production)
    "XLC":  ["Mercury", "Uranus"],                 # Communications: Mercury
    "XLK":  ["Mercury", "Uranus"],                 # Technology: Mercury+Uranus
    "XLP":  ["Moon", "Venus"],                     # Consumer Staples: Moon (daily necessities)
    "XLRE": ["Saturn", "Moon"],                    # Real Estate: Saturn (land)+Moon (home)
    "XLB":  ["Saturn", "Mars"],                    # Materials: Saturn+Mars
    "XLY":  ["Venus", "Sun"],                      # Consumer Disc: Venus (luxury, pleasure)
    "XLV":  ["Jupiter", "Neptune"],                # Healthcare: Jupiter (healing)+Neptune
    "KRE":  ["Jupiter", "Saturn"],                 # Regional Banks: Jupiter+Saturn
    "XBI":  ["Neptune", "Jupiter"],                # Biotech: Neptune (drugs)
    "JETS": ["Jupiter", "Uranus"],                 # Airlines: Jupiter (travel, long-distance)
    "ITB":  ["Saturn", "Venus"],                   # Homebuilders: Saturn (construction)
    "HACK": ["Uranus", "Mercury"],                 # Cybersecurity: Uranus (tech disruption)
    "TAN":  ["Sun", "Uranus"],                     # Solar: Sun (source of solar energy)
    "PAVE": ["Saturn", "Mars"],                    # Infrastructure: Saturn (structure)
    "XME":  ["Saturn", "Mars", "Venus"],           # Metals&Mining: Saturn+Mars
    "XOP":  ["Neptune", "Jupiter", "Mars"],        # Oil E&P: Neptune
}

print("="*90)
print(" FAILURE FORENSICS: ROOT CAUSE ANALYSIS FOR 24 REJECTED ASSETS")
print("="*90)

# ── Load astro matrix once ───────────────────────────────────────────────
print("\nLoading astro matrix...")
df_astro = pd.read_parquet(MATRIX_FILE)
df_astro["Date"] = pd.to_datetime(df_astro["Date"]).dt.tz_localize(None).astype("datetime64[us]")
if "Close"  in df_astro.columns: df_astro.drop(columns=["Close"],  inplace=True)
if "Volume" in df_astro.columns: df_astro.drop(columns=["Volume"], inplace=True)

# Identify feature groups per ruling planet
ALL_COLS = df_astro.columns.tolist()
def get_planet_cols(planets, all_cols):
    """Return columns that mention any of the ruling planets."""
    planet_cols = []
    for col in all_cols:
        col_upper = col.upper()
        for p in planets:
            if p.upper() in col_upper:
                planet_cols.append(col)
                break
    return planet_cols

results = {}
for asset_name, (ticker, bench) in ASSETS.items():
    print(f"\n--- {asset_name} ({ticker}/{bench}) ---")

    # Fetch price data
    try:
        df_a = yf.download(ticker, period="730d", interval="1h", progress=False, auto_adjust=False)
        df_b = yf.download(bench,  period="730d", interval="1h", progress=False, auto_adjust=False)
    except: continue
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

    fused = pd.merge_asof(syn.sort_values("Date"),
                          df_astro.sort_values("Date"),
                          on="Date", direction="backward")
    fused = fused.dropna(subset=["Tithi_Num"]).reset_index(drop=True)
    closes  = fused["Close"].values
    n       = len(closes)
    exclude = {"Close","Volume","dt","Date","index","Year","Quarter","label"}

    # Identify planet-specific features
    rulers = RULERSHIPS.get(asset_name, [])
    planet_cols = get_planet_cols(rulers, ALL_COLS)
    all_feat_cols = [c for c in fused.columns if c not in exclude and
                     fused[c].dtype in [np.float32,np.float64,np.int64,np.int32,int,float]]
    spec_feat_cols = [c for c in all_feat_cols if c in planet_cols]

    print(f"  Ruling planets: {rulers}")
    print(f"  Total features: {len(all_feat_cols)} | Planet-specific: {len(spec_feat_cols)}")
    print(f"  Spread spread (ATR proxy): {(fused['Close'].pct_change().abs().mean()*100):.4f}%/bar")

    # Test multiple barrier lengths
    barrier_results = {}
    for BARRIER in BARRIER_OPTIONS:
        labels = np.zeros(n, dtype=np.int8)
        for i in range(n - BARRIER):
            labels[i] = 1 if closes[i + BARRIER] > closes[i] else 0

        df2 = fused.copy()
        df2["label"] = labels
        df2 = df2.iloc[:-BARRIER].reset_index(drop=True)
        n2 = len(df2)
        X_all  = df2[all_feat_cols].fillna(0).values.astype(np.float32)
        X_spec = df2[spec_feat_cols].fillna(0).values.astype(np.float32) if spec_feat_cols else X_all
        y = df2["label"].values

        tscv = TimeSeriesSplit(n_splits=5)
        all_rets, spec_rets = [], []
        for tr, te in tscv.split(X_all):
            clean_tr = tr[:-BARRIER] if len(tr) > BARRIER else tr
            if len(clean_tr) < 50 or len(np.unique(y[clean_tr])) < 2: continue
            xp = dict(n_estimators=30, max_depth=3, learning_rate=0.05,
                      tree_method="hist", random_state=42, reg_alpha=1.5, reg_lambda=1.5)
            # Generic model
            m_all = xgb.XGBClassifier(**xp)
            m_all.fit(X_all[clean_tr], y[clean_tr], verbose=False)
            p_all = m_all.predict(X_all[te])
            # Planet-specific model
            if len(spec_feat_cols) >= 10:
                m_sp = xgb.XGBClassifier(**xp)
                m_sp.fit(X_spec[clean_tr], y[clean_tr], verbose=False)
                p_sp = m_sp.predict(X_spec[te])
            else:
                p_sp = p_all
            for i, idx in enumerate(te):
                if idx >= n2 - BARRIER: continue
                if p_all[i] == 1:
                    all_rets.append((closes[idx+BARRIER]/closes[idx])-1)
                if p_sp[i] == 1:
                    spec_rets.append((closes[idx+BARRIER]/closes[idx])-1)

        def cagr_from_rets(rets, years=2.9):
            if not rets: return -99.0
            eq = np.cumprod(1 + np.array(rets))
            return (eq[-1]**(1/years) - 1)*100

        bar_cagr_all  = cagr_from_rets(all_rets)
        bar_cagr_spec = cagr_from_rets(spec_rets)
        bar_wr_all    = (np.array(all_rets) > 0).mean()*100 if all_rets else 0
        barrier_results[BARRIER] = {
            "cagr_all": bar_cagr_all, "cagr_spec": bar_cagr_spec,
            "wr": bar_wr_all, "n_trades": len(all_rets)
        }
        print(f"  Barrier={BARRIER:2d}h | Generic CAGR={bar_cagr_all:+.1f}% | "
              f"PlanetSpec CAGR={bar_cagr_spec:+.1f}% | WR={bar_wr_all:.1f}% | Trades={len(all_rets)}")

    best_bar = max(barrier_results, key=lambda b: barrier_results[b]["cagr_spec"])
    best = barrier_results[best_bar]
    results[asset_name] = {
        "rulers": rulers, "n_planet_feats": len(spec_feat_cols),
        "best_barrier": best_bar, "best_cagr_spec": best["cagr_spec"],
        "best_cagr_all": best["cagr_all"],
        "improvement": best["cagr_spec"] - best["cagr_all"]
    }
    print(f"  >>> BEST: Barrier={best_bar}h | PlanetSpec={best['cagr_spec']:+.1f}% "
          f"vs Generic={best['cagr_all']:+.1f}% | Lift={best['cagr_spec']-best['cagr_all']:+.1f}%")

print("\n" + "="*90)
print(" SUMMARY: Planet-Specific Features × Optimal Barrier Lift")
print("="*90)
for asset, r in sorted(results.items(), key=lambda x: -x[1]["best_cagr_spec"]):
    flag = "FIXABLE" if r["best_cagr_spec"] > 10 else ("MARGINAL" if r["best_cagr_spec"] > 0 else "HARD")
    print(f"  {flag:8s}  {asset:<6}  Barrier={r['best_barrier']}h  "
          f"Generic={r['best_cagr_all']:+.1f}%  Spec={r['best_cagr_spec']:+.1f}%  "
          f"Lift={r['improvement']:+.1f}%  PlanetFeats={r['n_planet_feats']}  "
          f"Rulers={r['rulers']}")
