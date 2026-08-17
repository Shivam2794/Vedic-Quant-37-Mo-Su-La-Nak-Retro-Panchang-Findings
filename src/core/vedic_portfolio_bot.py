"""
VEDIC ALPHA PORTFOLIO EXECUTION DAEMON v3
==========================================
Clean final bot — 9 noise + quality gate approved assets.

Key improvements over v2:
  - DAILY DEDUPLICATION: Each asset fires at most ONE trade per calendar day.
    This matches the clean_backtest.py logic that produced the honest CAGR numbers.
  - Per-asset barriers loaded from {ASSET}_barrier.txt (3h / 6h / 12h / 24h)
  - Per-asset tier loaded from {ASSET}_tier.txt (1=full $10k, 2=half $5k)
  - Per-asset feature list loaded from {ASSET}_feature_names.txt
  - Hard spread guard: meta confidence < 52% → skip (no low-conviction trades)
  - Daily trade log: records each fired asset so dedup works across bot runs
"""
import os, warnings, numpy as np, pandas as pd, yfinance as yf, xgboost as xgb
from datetime import datetime, timezone, date
warnings.filterwarnings("ignore")

BASE_DIR    = r"C:\Users\patel\Desktop\Python\Learn"
MATRIX_FILE = os.path.join(BASE_DIR, "genesis_9000_MUNDANE.parquet")
MODELS_DIR  = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\models"
TRADE_LOG   = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\daily_trade_log.csv"

# ── FINAL 9-ASSET APPROVED UNIVERSE ────────────────────────────────────────
# Clean CAGR | MDD | Calmar | WR  (all from clean_backtest.py deduplication)
PAIRS = {
    # Tier 1: $10,000/leg
    "GLD":  ("GLD",  "SPY", 1),   # +249.8% | −53.5% | Calmar 4.67x | WR 67.9%
    "SMH":  ("SMH",  "SPY", 1),   #  +67.4% | −49.0% | Calmar 1.38x | WR 58.9%
    "COPX": ("COPX", "SPY", 1),   #  +56.9% | −35.7% | Calmar 1.59x | WR 54.6%
    "JETS": ("JETS", "SPY", 1),   #  +56.9% | −48.7% | Calmar 1.17x | WR 54.9%
    "XLC":  ("XLC",  "SPY", 1),   #  +27.5% | −28.9% | Calmar 0.95x | WR 53.5%
    "XLE":  ("XLE",  "SPY", 1),   #  +23.2% | −45.6% | Calmar 0.51x | WR 54.9%
    "CPER": ("CPER", "SPY", 1),   #  +12.5% | −27.7% | Calmar 0.45x | WR 52.8%
    # Tier 2: $5,000/leg (high CAGR but deep MDD — half-size)
    "SLV":  ("SLV",  "SPY", 2),   # +280.4% | −86.9% | Calmar 3.23x | WR 56.8% HALF
    "NLR":  ("NLR",  "SPY", 2),   #  +53.3% | −80.8% | Calmar 0.66x | WR 54.9% HALF
}

LIQUIDITY_SPREAD = {
    "NLR": 0.0015, "CPER": 0.0015, "SLV": 0.0008,
}
DEFAULT_SPREAD = 0.0005

META_CONFIDENCE_FLOOR = 0.52  # Skip any signal where meta P(correct) < 52%

def load_daily_trade_log():
    """Return set of asset names already traded today."""
    today = str(date.today())
    if not os.path.exists(TRADE_LOG): return set()
    try:
        df = pd.read_csv(TRADE_LOG)
        today_trades = df[df["date"] == today]["asset"].tolist()
        return set(today_trades)
    except: return set()

def record_trade(asset_name):
    """Append this asset to today's trade log."""
    today = str(date.today())
    row   = pd.DataFrame([{"date": today, "asset": asset_name,
                            "ts": datetime.now(timezone.utc).isoformat()}])
    if os.path.exists(TRADE_LOG):
        row.to_csv(TRADE_LOG, mode="a", header=False, index=False)
    else:
        row.to_csv(TRADE_LOG, index=False)

def load_asset_models(asset_name):
    """Load 4 models + metadata for an asset. Returns None if any missing."""
    md = MODELS_DIR
    files = [f"{asset_name}_primary.json", f"{asset_name}_meta.json",
             f"{asset_name}_max_up.json", f"{asset_name}_max_down.json",
             f"{asset_name}_feature_names.txt", f"{asset_name}_barrier.txt"]
    for f in files:
        if not os.path.exists(os.path.join(md, f)):
            return None
    primary   = xgb.XGBClassifier(); primary.load_model(os.path.join(md, f"{asset_name}_primary.json"))
    meta      = xgb.XGBClassifier(); meta.load_model(   os.path.join(md, f"{asset_name}_meta.json"))
    reg_up    = xgb.XGBRegressor(); reg_up.load_model(  os.path.join(md, f"{asset_name}_max_up.json"))
    reg_down  = xgb.XGBRegressor(); reg_down.load_model(os.path.join(md, f"{asset_name}_max_down.json"))
    with open(os.path.join(md, f"{asset_name}_feature_names.txt")) as f:
        feat_names = [l.strip() for l in f.readlines() if l.strip()]
    with open(os.path.join(md, f"{asset_name}_barrier.txt")) as f:
        barrier = int(f.read().strip())
    tier_file = os.path.join(md, f"{asset_name}_tier.txt")
    tier = int(open(tier_file).read().strip()) if os.path.exists(tier_file) else 1
    return primary, meta, reg_up, reg_down, feat_names, barrier, tier

def fetch_sync_price(asset, benchmark, lookback_bars=50):
    """Fetch latest hourly bars and compute spread close."""
    da = yf.download(asset,     period="5d", interval="1h", progress=False, auto_adjust=False)
    db = yf.download(benchmark, period="5d", interval="1h", progress=False, auto_adjust=False)
    if da.empty or db.empty: return None, None, None, None
    if isinstance(da.columns, pd.MultiIndex): da.columns = da.columns.get_level_values(0)
    if isinstance(db.columns, pd.MultiIndex): db.columns = db.columns.get_level_values(0)
    da = da[["Close","Volume"]].dropna()
    db = db[["Close"]].dropna()
    da, db = da.align(db, join="inner", axis=0)
    spread_close  = da["Close"] / db["Close"]
    asset_price   = da["Close"].iloc[-1]
    bench_price   = db["Close"].iloc[-1]
    spread_latest = spread_close.iloc[-1]
    return float(spread_latest), float(asset_price), float(bench_price), spread_close

def prepare_astro_row(df_astro, timestamp):
    """Return the astro feature row for the current timestamp."""
    ts = pd.Timestamp(timestamp).tz_localize(None) if hasattr(timestamp, 'tzinfo') and timestamp.tzinfo else pd.Timestamp(timestamp)
    ts_np = np.datetime64(ts.to_pydatetime().replace(tzinfo=None), 'us')
    idx = df_astro["Date"].searchsorted(ts_np, side="right") - 1
    if idx < 0: idx = 0
    return df_astro.iloc[idx]

print("="*72)
print("  VEDIC ALPHA PORTFOLIO EXECUTION DAEMON v3")
print("="*72)

now_utc = datetime.now(timezone.utc).replace(minute=30, second=0, microsecond=0)
print(f"\n[1] Session timestamp : {now_utc.isoformat()}")

# ── Load astro matrix ─────────────────────────────────────────────────────
print(f"\n[2] Loading mundane ephemeris...")
df_astro = pd.read_parquet(MATRIX_FILE)
df_astro["Date"] = pd.to_datetime(df_astro["Date"]).dt.tz_localize(None).astype("datetime64[us]")
for c in ["Close","Volume"]:
    if c in df_astro.columns: df_astro.drop(columns=[c], inplace=True)
print(f"    Loaded {len(df_astro):,} daily astro rows  ×  {len(df_astro.columns)} features")

# ── Daily dedup gate ──────────────────────────────────────────────────────
already_traded_today = load_daily_trade_log()
print(f"\n[3] Daily trade log: already fired today → {already_traded_today or '∅'}")

# ── Evaluate each asset ───────────────────────────────────────────────────
print(f"\n[4] Evaluating {len(PAIRS)}-asset universe...\n")

approved_trades = []

for asset_name, (ticker, bench, default_tier) in PAIRS.items():
    # ── Daily deduplication gate ────────────────────────────────────────
    if asset_name in already_traded_today:
        print(f"    {asset_name:<6} SKIP — already traded today (dedup gate)")
        continue

    # ── Load models ─────────────────────────────────────────────────────
    models = load_asset_models(asset_name)
    if models is None:
        print(f"    {asset_name:<6} SKIP — model files not found (run trainer v3 first)")
        continue
    primary, meta, reg_up, reg_down, feat_names, BARRIER, tier = models
    capital = 10000.0 if tier == 1 else 5000.0

    # ── Fetch prices ────────────────────────────────────────────────────
    spread_val, asset_px, bench_px, spread_series = fetch_sync_price(ticker, bench)
    if spread_val is None:
        print(f"    {asset_name:<6} SKIP — price fetch failed")
        continue

    # ── Build feature vector ─────────────────────────────────────────────
    astro_row = prepare_astro_row(df_astro, now_utc)
    feat_dict = {}
    for fn in feat_names:
        feat_dict[fn] = float(astro_row[fn]) if fn in astro_row.index else 0.0
    X = np.array([[feat_dict.get(fn, 0.0) for fn in feat_names]], dtype=np.float32)

    # ── Primary classification ───────────────────────────────────────────
    direction_pred = int(primary.predict(X)[0])
    direction      = "LONG" if direction_pred == 1 else "SHORT"

    # ── Meta confidence (P that primary is correct) ──────────────────────
    pp   = primary.predict_proba(X)[:, 1]
    mX   = np.column_stack([pp, X[:, :min(50, X.shape[1])]])
    meta_conf = float(meta.predict_proba(mX)[0, 1])

    if meta_conf < META_CONFIDENCE_FLOOR:
        print(f"    {asset_name:<6} SKIP — meta confidence {meta_conf:.1%} < {META_CONFIDENCE_FLOOR:.0%} floor")
        continue

    # ── Excursion forecasts ───────────────────────────────────────────────
    mfe = float(reg_up.predict(X)[0])
    mae = float(reg_down.predict(X)[0])
    mfe = max(mfe, 0.003)  # floor 0.3%
    mae = max(mae, 0.003)

    # ── Position sizing ───────────────────────────────────────────────────
    asset_shares  = round(capital / asset_px, 4) if asset_px > 0 else 0
    bench_shares  = round(capital / bench_px, 4) if bench_px > 0 else 0
    stop_loss_usd = round(-capital * mae, 2)
    take_profit_usd = round(capital * mfe, 2)

    # ── Limit spread tolerance ────────────────────────────────────────────
    spread_tol = LIQUIDITY_SPREAD.get(asset_name, DEFAULT_SPREAD)
    fill_time  = "15 Min Fill-or-Kill"

    approved_trades.append({
        "asset": asset_name, "direction": direction,
        "meta": meta_conf, "mfe": mfe, "mae": mae,
        "tier": tier, "barrier_h": BARRIER,
        "asset_px": asset_px, "bench_px": bench_px,
        "asset_shares": asset_shares, "bench_shares": bench_shares,
        "capital": capital, "stop": stop_loss_usd, "tp": take_profit_usd,
        "spread_tol": spread_tol, "fill_time": "15 Min Fill-or-Kill",
        "ticker": ticker, "bench": bench,
    })

# ── Print execution directives ────────────────────────────────────────────
print("="*72)
print(f"  EXECUTION DIRECTIVES  ({len(approved_trades)} Approved — "
      f"{len(PAIRS)-len(approved_trades)} Filtered)")
print("="*72)

if not approved_trades:
    print("\n  No signals passed all gates today. No trades recommended.")
else:
    for t in approved_trades:
        leg1 = ("BUY " if t["direction"]=="LONG" else "SELL")
        leg2 = ("SELL" if t["direction"]=="LONG" else "BUY ")
        print(f"\n  >>> {t['asset']} | {t['direction']} | "
              f"Meta={t['meta']:.1%} | Barrier={t['barrier_h']}h | "
              f"Tier={t['tier']} (${t['capital']:,.0f}/leg) <<<")
        print(f"    MFE: +{t['mfe']*100:.2f}%  MAE: -{t['mae']*100:.2f}%")
        print(f"    [1] {leg1} ${t['capital']:,.0f} of {t['ticker']} "
              f"@ ${t['asset_px']:.2f}  ({t['asset_shares']} shrs)")
        print(f"    [2] {leg2} ${t['capital']:,.0f} of {t['bench']} "
              f"@ ${t['bench_px']:.2f}  ({t['bench_shares']} shrs)")
        print(f"    [3] Limit Spread Tolerance: {t['spread_tol']*100:.3f}%  ({t['fill_time']})")
        print(f"    [4] Stop-Loss: ${t['stop']:+,.2f}  |  Take-Profit: ${t['tp']:+,.2f}")
        # Record in daily log to enforce deduplication
        record_trade(t["asset"])

print(f"\n  [Daily dedup log updated: {str(date.today())}]")
print("="*72)
