import os, numpy as np, pandas as pd, yfinance as yf, xgboost as xgb, warnings
warnings.filterwarnings('ignore')

BASE_DIR = r"C:\Users\patel\Desktop\Python\Learn"
models_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\models"
MATRIX_FILE = os.path.join(BASE_DIR, "genesis_9000_MUNDANE.parquet")
BARRIER_BARS = 6

# ── CHECK A: label distribution per asset ─────────────────────────────────
print("=== LABEL DISTRIBUTION CHECK ===")
assets = ['COPX','XLC','XLF','XLI','PAVE','SMH','JETS','SLV']
for asset in assets:
    df_asset = yf.download(asset, period="730d", interval="1h", progress=False, auto_adjust=False)
    df_spy   = yf.download("SPY",  period="730d", interval="1h", progress=False, auto_adjust=False)
    if isinstance(df_asset.columns, pd.MultiIndex): df_asset.columns = df_asset.columns.get_level_values(0)
    if isinstance(df_spy.columns,   pd.MultiIndex): df_spy.columns   = df_spy.columns.get_level_values(0)
    df_asset = df_asset[["Close","Volume"]].dropna()
    df_spy   = df_spy[["Close"]].dropna()
    da, db = df_asset.align(df_spy, join='inner', axis=0)
    syn = pd.DataFrame()
    syn["Close"]  = da["Close"] / db["Close"]
    syn["Volume"] = da["Volume"]
    syn["dt"]     = syn.index
    mask = (syn.index.hour >= 9) & (syn.index.hour <= 15)
    syn  = syn[mask].reset_index(drop=True)
    closes = syn["Close"].values
    n = len(closes)
    labels = np.array([1 if closes[min(i+BARRIER_BARS, n-1)] > closes[i] else 0 for i in range(n-BARRIER_BARS)])
    pct = labels.mean()*100
    print(f"  {asset}: {n} rows | LONG={pct:.1f}% SHORT={(100-pct):.1f}%")

# ── CHECK B: astro matrix date coverage ───────────────────────────────────
print()
print("=== ASTRO MATRIX DATE COVERAGE ===")
df_astro = pd.read_parquet(MATRIX_FILE)
df_astro["Date"] = pd.to_datetime(df_astro["Date"]).dt.tz_localize(None)
print(f"  Astro start: {df_astro['Date'].min().date()}")
print(f"  Astro end:   {df_astro['Date'].max().date()}")
print(f"  Astro rows:  {len(df_astro)}")
print(f"  NaN cols >5%: {(df_astro.isna().mean()>0.05).sum()}")

# ── CHECK C: merge coverage on COPX ──────────────────────────────────────
print()
print("=== MERGE COVERAGE CHECK (COPX) ===")
df_asset = yf.download("COPX", period="730d", interval="1h", progress=False, auto_adjust=False)
df_spy   = yf.download("SPY",  period="730d", interval="1h", progress=False, auto_adjust=False)
if isinstance(df_asset.columns, pd.MultiIndex): df_asset.columns = df_asset.columns.get_level_values(0)
if isinstance(df_spy.columns,   pd.MultiIndex): df_spy.columns   = df_spy.columns.get_level_values(0)
df_asset = df_asset[["Close","Volume"]].dropna()
df_spy   = df_spy[["Close"]].dropna()
da, db = df_asset.align(df_spy, join='inner', axis=0)
syn = pd.DataFrame()
syn["Close"]  = da["Close"] / db["Close"]
syn["Volume"] = da["Volume"]
syn["dt"]     = syn.index
mask = (syn.index.hour >= 9) & (syn.index.hour <= 15)
syn  = syn[mask].reset_index(drop=True)
syn["Date"] = pd.to_datetime(syn["dt"]).dt.tz_localize(None).astype("datetime64[us]")
df_astro2 = df_astro.copy()
df_astro2["Date"] = df_astro2["Date"].astype("datetime64[us]")
fused = pd.merge_asof(syn.sort_values("Date"), df_astro2.sort_values("Date"), on="Date", direction="backward")
fill_pct = fused["Tithi_Num"].notna().mean()*100 if "Tithi_Num" in fused.columns else 0
print(f"  COPX rows before merge: {len(syn)}")
print(f"  COPX rows after merge: {len(fused)}")
print(f"  Astro fill rate: {fill_pct:.1f}%")

# ── CHECK D: Suspicious tiny models (degenerate early stopping) ──────────
print()
print("=== SUSPICIOUS TINY MODEL INSPECTION ===")
tiny_models = [
    "XLC_max_down.json","XLC_max_up.json",
    "XLF_max_down.json","XLF_max_up.json",
    "XLI_max_down.json","XLI_max_up.json",
    "XLK_max_up.json","PAVE_max_down.json"
]
for fname in tiny_models:
    path = os.path.join(models_dir, fname)
    m = xgb.XGBRegressor()
    m.load_model(path)
    dump = m.get_booster().get_dump()
    print(f"  {fname}: {len(dump)} trees | size={os.path.getsize(path)} bytes")

print()
print("=== COMPLETE ===")
