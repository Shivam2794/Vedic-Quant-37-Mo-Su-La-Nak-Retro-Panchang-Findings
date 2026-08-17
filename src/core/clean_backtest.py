"""
OVERFITTING ROOT CAUSE ANALYSIS + CLEAN REBUILD
================================================
THE BUG: Intraday bar overlap at BARRIER > 6h

When BARRIER=24h with hourly data (7 bars/day):
  - Bar at 9am fires LONG → exits at 9am NEXT DAY (bar i+24)
  - Bar at 10am fires LONG → exits at 10am NEXT DAY (bar i+24)
  - These overlap completely — same planetary features, nearly same prices
  - The WFO compounds ALL of them as independent $10k trades
  - 7 bars/day × high WR = 7x overcounting of daily returns
  - Result: +44,481% holdout "CAGR" for GLD — PHYSICALLY IMPOSSIBLE

THE PROOF:
  - GLD WFO (in-sample 85%) = +192% → honest-looking
  - GLD holdout (out-of-sample 15%) = +44,481% → IMPOSSIBLE
  - The holdout period is ~4-5 months (15% of 730 days)
  - Even +192% would need months of massive compound wins
  - +44,481% in ~4 months = COMPLETE overcount of overlapping bars

THE FIX: For any BARRIER > 6h, deduplicate to ONE SIGNAL PER TRADING DAY.
  - Only take the first signal fired per calendar date
  - This eliminates the overlap and gives the true per-day return

THE DEEPER FIX: 
  - BARRIER=6h is CLEAN because 6 bars = ~1 trading day of 7 bars
  - There IS some overlap at 6h too (bars fired at 2pm and 3pm would both target
    the following day's 2pm and 3pm) but at 6h the returns are mostly intraday
    and the duplication is 1/7 of trades
  - For safety, apply daily deduplication at ALL barrier levels
  - This gives a clean "maximum one trade per day per asset" logic
  - CAGR computed on deduplicated returns = honest backtest

WHAT HAPPENS TO THE NEW ASSETS AFTER DEDUPLICATION:
  - 24h barrier assets (SLV, GLD, NLR, JETS, XOP): ~1 trade/day → real CAGR
  - 12h barrier assets (XME, XBI, XLC, XLE): ~0.5 trade/day → real CAGR
  - 6h barrier (COPX, CPER, SMH, XLU, HACK): ~1 trade/day → real CAGR  
  - 3h barrier (PAVE, URA, XLI): ~2 trades/day → some overlap remains

Let's compute the TRUE deduplicated CAGR for all assets.
"""
import os, numpy as np, pandas as pd, yfinance as yf, xgboost as xgb, warnings
warnings.filterwarnings("ignore")
from sklearn.model_selection import TimeSeriesSplit

BASE_DIR   = r"C:\Users\patel\Desktop\Python\Learn"
MATRIX_FILE = os.path.join(BASE_DIR, "genesis_9000_MUNDANE.parquet")

# Full universe to test cleanly
ASSETS = {
    # Tier 1 originals
    "COPX": ("COPX", "SPY",  6, []),
    "CPER": ("CPER", "SPY",  6, []),
    "SMH":  ("SMH",  "SPY",  6, []),
    "XLU":  ("XLU",  "SPY",  6, []),
    # Tier 2 candidates
    "XME":  ("XME",  "SPY", 12, []),
    "XBI":  ("XBI",  "SPY", 12, []),
    "XLC":  ("XLC",  "SPY", 12, []),
    "XLE":  ("XLE",  "SPY", 12, []),
    "HACK": ("HACK", "SPY",  6, []),
    "GLD":  ("GLD",  "SPY", 24, ["Sun","Venus","Jupiter"]),
    "SLV":  ("SLV",  "SPY", 24, []),
    "NLR":  ("NLR",  "SPY", 24, []),
    "JETS": ("JETS", "SPY", 24, []),
    "XOP":  ("XOP",  "SPY", 24, []),
    "PAVE": ("PAVE", "SPY",  3, []),
    "URA":  ("URA",  "SPY",  3, []),
    "XLI":  ("XLI",  "SPY",  3, []),
}

def get_planet_cols(rulers, all_cols):
    if not rulers: return all_cols
    planet = [c for c in all_cols if any(r.upper() in c.upper() for r in rulers)]
    panchang = [c for c in all_cols if any(k in c for k in
                ["Tithi","Nakshatra","Yoga","Karana","Vara","Pushkar","asc_"])]
    combined = list(set(planet + panchang))
    return combined if len(combined) >= 20 else all_cols

print("="*90)
print(" CLEAN BACKTEST: Daily-Deduplicated Returns (One Trade Per Day Max)")
print(" This eliminates the intraday overlap overcounting bug.")
print("="*90)

df_astro = pd.read_parquet(MATRIX_FILE)
df_astro["Date"] = pd.to_datetime(df_astro["Date"]).dt.tz_localize(None).astype("datetime64[us]")
for c in ["Close","Volume"]:
    if c in df_astro.columns: df_astro.drop(columns=[c], inplace=True)

results = {}
XP = dict(n_estimators=30, max_depth=3, learning_rate=0.05,
          tree_method="hist", random_state=42, reg_alpha=1.5, reg_lambda=1.5)

for asset_name, (ticker, bench, BARRIER, rulers) in ASSETS.items():
    print(f"\n{'─'*60}")
    print(f" {asset_name}  barrier={BARRIER}h  rulers={rulers or 'ALL'}")
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
    syn["date_only"] = pd.to_datetime(syn.index).date  # ← KEY: calendar date for dedup
    mask = (syn.index.hour >= 9) & (syn.index.hour <= 15)
    syn  = syn[mask].reset_index(drop=True)
    syn["Date"] = pd.to_datetime(syn["dt"]).dt.tz_localize(None).astype("datetime64[us]")

    fused = pd.merge_asof(syn.sort_values("Date"), df_astro.sort_values("Date"),
                          on="Date", direction="backward")
    fused = fused.dropna(subset=["Tithi_Num"]).reset_index(drop=True)

    closes = fused["Close"].values
    dates  = fused["date_only"].values if "date_only" in fused.columns else \
             np.array([str(fused["dt"].iloc[i].date()) for i in range(len(fused))])
    n = len(closes)

    exclude = {"Close","Volume","dt","Date","date_only","index","label"}
    all_feat = [c for c in fused.columns if c not in exclude and
                fused[c].dtype in [np.float32,np.float64,np.int64,np.int32,int,float]]
    feat_cols = get_planet_cols(rulers, all_feat)

    # Labels: simple binary
    labels = np.zeros(n, dtype=np.int8)
    for i in range(n - BARRIER):
        labels[i] = 1 if closes[i + BARRIER] > closes[i] else 0
    fused["label"] = labels
    df2 = fused.iloc[:-BARRIER].reset_index(drop=True)
    n2  = len(df2)

    X = df2[feat_cols].fillna(0).values.astype(np.float32)
    y = df2["label"].values
    cl = df2["Close"].values
    dt = df2["date_only"].values if "date_only" in df2.columns else \
         np.array([str(df2["dt"].iloc[i].date()) for i in range(n2)])

    tscv = TimeSeriesSplit(n_splits=5)

    # ── NAIVE (old, overcounted) ─────────────────────────────────────
    naive_rets = []
    # ── CLEAN (deduplicated: one trade per calendar date) ────────────
    clean_rets = []

    for tr, te in tscv.split(X):
        clean_tr = tr[:-BARRIER] if len(tr) > BARRIER else tr
        if len(clean_tr) < 30 or len(np.unique(y[clean_tr])) < 2: continue
        m = xgb.XGBClassifier(**XP)
        m.fit(X[clean_tr], y[clean_tr], verbose=False)
        preds = m.predict(X[te])

        seen_dates_this_fold = set()
        for i, idx in enumerate(te):
            if idx >= n2 - BARRIER: continue
            move = (cl[idx + BARRIER] / cl[idx]) - 1.0
            # Naive: every bar fires independently
            if preds[i] == 1:
                naive_rets.append(move)
            # Clean: only first signal per calendar date
            if preds[i] == 1:
                day = str(dt[idx])
                if day not in seen_dates_this_fold:
                    seen_dates_this_fold.add(day)
                    clean_rets.append(move)

    def cagr(rets, years=2.9):
        if not rets: return -99.0
        arr = np.array(rets)
        eq  = np.cumprod(1 + arr)
        return round((eq[-1]**(1/years) - 1)*100, 1)

    def mdd(rets):
        if not rets: return 0.0
        eq  = np.cumprod(1 + np.array(rets))
        pk  = np.maximum.accumulate(eq)
        dd  = (eq - pk) / pk
        return round(dd.min()*100, 1)

    naive_c = cagr(naive_rets)
    clean_c = cagr(clean_rets)
    naive_m = mdd(naive_rets)
    clean_m = mdd(clean_rets)
    naive_wr = round((np.array(naive_rets)>0).mean()*100, 1) if naive_rets else 0
    clean_wr = round((np.array(clean_rets)>0).mean()*100, 1) if clean_rets else 0
    overcount = round(len(naive_rets) / max(len(clean_rets), 1), 1)

    print(f"  Bars={n}  Features={len(feat_cols)}")
    print(f"  NAIVE (overcounted):  CAGR={naive_c:+.1f}%  MDD={naive_m:.1f}%  "
          f"WR={naive_wr}%  Trades={len(naive_rets)}")
    print(f"  CLEAN (1/day):        CAGR={clean_c:+.1f}%  MDD={clean_m:.1f}%  "
          f"WR={clean_wr}%  Trades={len(clean_rets)}")
    print(f"  Overcount factor: {overcount}x  |  Inflation ratio: "
          f"{round(naive_c/max(abs(clean_c),0.01),1) if clean_c!=0 else 'N/A'}x CAGR")

    results[asset_name] = {
        "barrier": BARRIER,
        "naive_cagr": naive_c, "clean_cagr": clean_c,
        "naive_mdd":  naive_m, "clean_mdd":  clean_m,
        "naive_wr":   naive_wr,"clean_wr":   clean_wr,
        "n_naive":    len(naive_rets), "n_clean": len(clean_rets),
        "overcount":  overcount,
    }

print("\n" + "="*90)
print(" MASTER TRUTH TABLE: Naive vs Clean CAGR for All Assets")
print("="*90)
print(f"{'ASSET':<6} {'BAR':>4} {'NAIVE CAGR':>11} {'CLEAN CAGR':>11} "
      f"{'CLEAN MDD':>10} {'CLEAN WR':>9} {'OVERCOUNT':>10} {'VERDICT':>12}")
print("-"*90)

final_approved = []
for asset, r in sorted(results.items(), key=lambda x: -x[1]["clean_cagr"]):
    verdict = ("TRADE ✅" if r["clean_cagr"] > 5 else
               "MARGINAL ⚠️" if r["clean_cagr"] > 0 else "REJECT ❌")
    if r["clean_cagr"] > 5: final_approved.append((asset, r))
    print(f"{asset:<6} {r['barrier']:>3}h {r['naive_cagr']:>+10.1f}% {r['clean_cagr']:>+10.1f}% "
          f"{r['clean_mdd']:>9.1f}% {r['clean_wr']:>8.1f}% {r['overcount']:>9.1f}x "
          f"{verdict:>12}")

print(f"\nFINAL CLEAN APPROVED UNIVERSE: {len(final_approved)} assets")
for asset, r in sorted(final_approved, key=lambda x: -x[1]["clean_cagr"]):
    calmar = r["clean_cagr"] / abs(r["clean_mdd"]) if r["clean_mdd"] != 0 else 0
    print(f"  ✅ {asset:<6}  Clean CAGR={r['clean_cagr']:+.1f}%  "
          f"MDD={r['clean_mdd']:.1f}%  Calmar={calmar:+.2f}x  "
          f"Overcount was {r['overcount']}x")
