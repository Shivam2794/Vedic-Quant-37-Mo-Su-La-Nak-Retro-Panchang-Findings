"""
MASTER BACKTEST: All tested + all new assets.
Clean daily deduplication throughout.
Two modes:
  - HOURLY (existing assets): 1h bars, deduplicated 1/day
  - DAILY (new + existing with 21yr data): 1d bars, no overlap possible
Reports clean CAGR, MDD, Calmar, WR, noise delta for every asset.
"""
import os, numpy as np, pandas as pd, yfinance as yf, xgboost as xgb, warnings
warnings.filterwarnings("ignore")
from sklearn.model_selection import TimeSeriesSplit

BASE_DIR    = r"C:\Users\patel\Desktop\Python\Learn"
MATRIX_FILE = os.path.join(BASE_DIR, "supreme_genesis_matrix.parquet")

# ── COMPLETE UNIVERSE ────────────────────────────────────────────────────────
# (ticker, bench, barrier_h, rulers, use_daily, note)
UNIVERSE = {
    # ── Original 9 approved ─────────────────────────────────────────────────
    "GLD":  ("GLD",  "SPY", 24, ["Sun","Venus","Jupiter"], False, "APPROVED T1"),
    "SLV":  ("SLV",  "SPY", 24, [],                        False, "APPROVED T2"),
    "SMH":  ("SMH",  "SPY",  6, [],                        False, "APPROVED T1"),
    "COPX": ("COPX", "SPY",  6, [],                        False, "APPROVED T1"),
    "JETS": ("JETS", "SPY", 24, [],                        False, "APPROVED T1 WATCH"),
    "NLR":  ("NLR",  "SPY", 24, [],                        False, "APPROVED T2"),
    "XLC":  ("XLC",  "SPY", 12, [],                        False, "APPROVED T1"),
    "XLE":  ("XLE",  "SPY", 12, [],                        False, "APPROVED T1 WATCH"),
    "CPER": ("CPER", "SPY",  6, [],                        False, "APPROVED T1"),
    # ── Previously rejected (re-verify with clean pipeline) ─────────────────
    "XME":  ("XME",  "SPY", 12, [],                        False, "REJECTED MDD"),
    "XBI":  ("XBI",  "SPY", 12, [],                        False, "REJECTED WR"),
    "XOP":  ("XOP",  "SPY", 24, [],                        False, "REJECTED WR"),
    "PAVE": ("PAVE", "SPY",  3, [],                        False, "REJECTED CAGR"),
    "URA":  ("URA",  "SPY",  3, [],                        False, "REJECTED CAGR"),
    "HACK": ("HACK", "SPY",  6, [],                        False, "REJECTED CAGR"),
    "XLI":  ("XLI",  "SPY",  3, [],                        False, "REJECTED CAGR"),
    "XLU":  ("XLU",  "SPY",  6, [],                        False, "REJECTED WR"),
    "GDX":  ("GDX",  "SPY", 12, ["Sun","Venus","Saturn"],  False, "REJECTED NOISE"),
    "XLK":  ("XLK",  "SPY",  6, [],                        False, "REJECTED NOISE"),
    "TAN":  ("TAN",  "SPY",  6, [],                        False, "REJECTED"),
    "XLF":  ("XLF",  "SPY",  6, [],                        False, "REJECTED"),
    "XLP":  ("XLP",  "SPY",  6, [],                        False, "REJECTED"),
    "XLY":  ("XLY",  "SPY",  6, [],                        False, "REJECTED"),
    "XLB":  ("XLB",  "SPY",  6, [],                        False, "REJECTED"),
    "XLRE": ("XLRE", "SPY",  6, [],                        False, "REJECTED"),
    "XLV":  ("XLV",  "SPY",  6, [],                        False, "REJECTED"),
    "KRE":  ("KRE",  "SPY",  6, [],                        False, "REJECTED"),
    "ITB":  ("ITB",  "SPY",  6, [],                        False, "REJECTED"),
    # ── NEW: Never tested ───────────────────────────────────────────────────
    "QQQ":  ("QQQ",  "SPY",  6, [],                        False, "NEW-INDEX"),
    "DIA":  ("DIA",  "SPY",  6, [],                        False, "NEW-INDEX"),
    "IWM":  ("IWM",  "SPY",  6, [],                        False, "NEW-INDEX"),
    "TLT":  ("TLT",  "SPY", 12, [],                        False, "NEW-BOND"),
    "HYG":  ("HYG",  "SPY",  6, [],                        False, "NEW-BOND"),
    "DBA":  ("DBA",  "SPY", 24, ["Moon"],                  False, "NEW-AGRI"),
    "USO":  ("USO",  "SPY", 12, [],                        False, "NEW-OIL"),
    "UNG":  ("UNG",  "SPY", 12, [],                        False, "NEW-GAS"),
    "EEM":  ("EEM",  "SPY",  6, [],                        False, "NEW-EM"),
    "PPLT": ("PPLT", "SPY", 12, [],                        False, "NEW-PLAT"),
    "ARKK": ("ARKK", "SPY",  6, [],                        False, "NEW-THEME"),
}

XP = dict(n_estimators=30, max_depth=3, learning_rate=0.05,
          tree_method="hist", random_state=42,
          reg_alpha=1.5, reg_lambda=1.5, min_child_weight=5)

def get_planet_cols(rulers, all_cols):
    if not rulers: return all_cols
    p = [c for c in all_cols if any(r.upper() in c.upper() for r in rulers)]
    pan = [c for c in all_cols if any(k in c for k in ["Tithi","Nakshatra","Yoga","Karana"])]
    sel = list(set(p + pan))
    return sel if len(sel) >= 20 else all_cols

def clean_wfo(X, y, cl, dt, BARRIER, n_splits=5):
    tscv = TimeSeriesSplit(n_splits=n_splits)
    real_rets, noise_rets = [], []
    rng = np.random.RandomState(42)
    X_noise = rng.randn(*X.shape).astype(np.float32)
    n2 = len(X)
    for tr, te in tscv.split(X):
        clean_tr = tr[:-BARRIER] if len(tr) > BARRIER else tr
        if len(clean_tr) < 30 or len(np.unique(y[clean_tr])) < 2: continue
        # Real
        mr = xgb.XGBClassifier(**XP); mr.fit(X[clean_tr], y[clean_tr], verbose=False)
        pr = mr.predict(X[te])
        # Noise
        mn = xgb.XGBClassifier(**XP); mn.fit(X_noise[clean_tr], y[clean_tr], verbose=False)
        pn = mn.predict(X_noise[te])
        seen_r, seen_n = set(), set()
        for i, idx in enumerate(te):
            if idx >= n2 - BARRIER: continue
            move = (cl[idx+BARRIER] / cl[idx]) - 1.0
            day  = str(dt[idx])
            if pr[i] == 1 and day not in seen_r:
                seen_r.add(day); real_rets.append(move)
            if pn[i] == 1 and day not in seen_n:
                seen_n.add(day); noise_rets.append(move)
    return real_rets, noise_rets

def metrics(rets, years=2.9):
    if not rets: return -99.0, 0.0, 0.0, 0
    arr = np.array(rets)
    eq  = np.cumprod(1 + arr)
    cagr_val = round((eq[-1]**(1/years) - 1)*100, 1)
    pk   = np.maximum.accumulate(eq)
    mdd  = round(((eq - pk)/pk).min()*100, 1)
    wr   = round((arr > 0).mean()*100, 1)
    return cagr_val, mdd, wr, len(rets)

print("="*100)
print(" MASTER BACKTEST: All 39 Assets | Clean Deduplication | Noise Gate | Quality Gates")
print("="*100)

df_astro = pd.read_parquet(MATRIX_FILE)
df_astro["Date"] = pd.to_datetime(df_astro["Date"]).dt.tz_localize(None).astype("datetime64[us]")
for c in ["Close","Volume"]:
    if c in df_astro.columns: df_astro.drop(columns=[c], inplace=True)

all_results = {}

for asset_name, (ticker, bench, BARRIER, rulers, use_daily, note) in UNIVERSE.items():
    try:
        period = "730d"
        interval = "1h"
        df_a = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=False)
        df_b = yf.download(bench,  period=period, interval=interval, progress=False, auto_adjust=False)
        if df_a.empty or df_b.empty: raise ValueError("empty")
    except:
        all_results[asset_name] = None; print(f"  {asset_name:<6} SKIP (download failed)"); continue

    if isinstance(df_a.columns, pd.MultiIndex): df_a.columns = df_a.columns.get_level_values(0)
    if isinstance(df_b.columns, pd.MultiIndex): df_b.columns = df_b.columns.get_level_values(0)
    df_a = df_a[["Close"]].dropna(); df_b = df_b[["Close"]].dropna()
    da, db = df_a.align(df_b, join="inner", axis=0)
    syn = pd.DataFrame({"Close": da["Close"]/db["Close"]})
    syn["dt"]   = syn.index
    mask = (syn.index.hour >= 9) & (syn.index.hour <= 15)
    syn  = syn[mask].reset_index(drop=True)
    syn["date_only"] = pd.to_datetime(syn["dt"]).dt.date.astype(str)
    syn["Date"] = pd.to_datetime(syn["dt"]).dt.tz_localize(None).astype("datetime64[us]")

    fused = pd.merge_asof(syn.sort_values("Date"), df_astro.sort_values("Date"),
                          on="Date", direction="backward")
    fused = fused.dropna(subset=["Tithi_Num"]).reset_index(drop=True)
    closes = fused["Close"].values
    dates  = fused["date_only"].values
    n = len(closes)

    exclude = {"Close","dt","Date","date_only","index","label"}
    all_feat = [c for c in fused.columns if c not in exclude and
                fused[c].dtype in [np.float32,np.float64,np.int64,np.int32,int,float]]
    feat_cols = get_planet_cols(rulers, all_feat)

    labels = np.zeros(n, dtype=np.int8)
    for i in range(n - BARRIER): labels[i] = 1 if closes[i+BARRIER] > closes[i] else 0
    fused["label"] = labels
    df2 = fused.iloc[:-BARRIER].reset_index(drop=True)
    X = df2[feat_cols].fillna(0).values.astype(np.float32)
    y = df2["label"].values
    cl = df2["Close"].values
    dt = df2["date_only"].values
    n2 = len(df2)

    real_rets, noise_rets = clean_wfo(X, y, cl, dt, BARRIER)
    rc, rm, rw, rn = metrics(real_rets)
    nc, nm, nw, nn = metrics(noise_rets)
    delta = rc - nc
    calmar = round(rc / abs(rm), 2) if rm != 0 else 0.0

    # Quality gate verdict
    noise_pass = delta > 0
    if not noise_pass:                             verdict = "NOISE FAIL ❌"
    elif rc < 5:                                   verdict = "CAGR LOW ❌"
    elif rm < -87:                                 verdict = "MDD DEEP ❌"
    elif calmar < 0.40:                            verdict = "CALMAR LOW ❌"
    elif rw < 50.0:                                verdict = "WR LOW ❌"
    else:                                          verdict = "PASS ✅"

    all_results[asset_name] = {
        "real_cagr": rc, "real_mdd": rm, "real_wr": rw,
        "noise_cagr": nc, "noise_delta": delta,
        "calmar": calmar, "n_trades": rn,
        "barrier": BARRIER, "note": note, "verdict": verdict,
    }
    print(f"  {asset_name:<6}  {rc:>+7.1f}%  MDD{rm:>7.1f}%  Cal{calmar:>+5.2f}x  "
          f"WR{rw:>5.1f}%  Noise Δ{delta:>+8.1f}%  {verdict}  [{note}]")

# ── MASTER REPORT ──────────────────────────────────────────────────────────
valid = {k: v for k, v in all_results.items() if v is not None}
print("\n" + "="*100)
print(" MASTER QUALITY REPORT — All 39 Assets, All Lenses")
print("="*100)
print(f"{'ASSET':<6} {'CAGR':>8} {'MDD':>8} {'CALMAR':>7} {'WR':>6} "
      f"{'NOISE Δ':>9} {'BAR':>4} {'VERDICT':<18} {'CATEGORY'}")
print("-"*100)
for asset, r in sorted(valid.items(), key=lambda x: -x[1]["real_cagr"]):
    print(f"{asset:<6} {r['real_cagr']:>+7.1f}% {r['real_mdd']:>+7.1f}% "
          f"{r['calmar']:>+6.2f}x {r['real_wr']:>5.1f}% "
          f"{r['noise_delta']:>+8.1f}% {r['barrier']:>3}h "
          f"{r['verdict']:<18} {r['note']}")

passed = [(k,v) for k,v in valid.items() if v["verdict"]=="PASS ✅"]
print(f"\n{'='*50}")
print(f" NEW PASS: {len(passed)} assets cleared ALL gates")
print(f"{'='*50}")
for k, v in sorted(passed, key=lambda x: -x[1]["real_cagr"]):
    print(f"  ✅ {k:<6}  CAGR={v['real_cagr']:+.1f}%  MDD={v['real_mdd']:.1f}%  "
          f"Calmar={v['calmar']:+.2f}x  WR={v['real_wr']:.1f}%  "
          f"NoiseΔ={v['noise_delta']:+.1f}%")
