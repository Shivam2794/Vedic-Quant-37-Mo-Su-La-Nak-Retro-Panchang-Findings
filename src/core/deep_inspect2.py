"""
Deep Inspection Part 2:
- MFE sign check (can regressors predict negative MFE?)
- Meta-model class balance (can meta_targ be all-one-class?)
- Live bot tz-handling on after-hours/weekend runs
- Dollar-neutrality drift quantification
- Feature column ordering consistency across assets
"""
import os, numpy as np, pandas as pd, yfinance as yf, xgboost as xgb, warnings
warnings.filterwarnings('ignore')

BASE_DIR  = r"C:\Users\patel\Desktop\Python\Learn"
models_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\models"
MATRIX_FILE = os.path.join(BASE_DIR, "genesis_9000_MUNDANE.parquet")
BARRIER_BARS = 6

# ── CHECK E: MFE/MAE prediction ranges for degenerate assets ─────────────
print("=== MFE/MAE PREDICTION RANGE CHECK (degenerate models) ===")
degenerate = ["XLC","XLF","XLI","PAVE"]
for asset in degenerate:
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
    max_ups   = np.array([(np.max(closes[i+1:i+1+BARRIER_BARS])/closes[i])-1 for i in range(n-BARRIER_BARS)])
    max_downs = np.array([1-(np.min(closes[i+1:i+1+BARRIER_BARS])/closes[i]) for i in range(n-BARRIER_BARS)])
    
    # Load the degenerate model and check prediction range
    reg_up = xgb.XGBRegressor()
    reg_up.load_model(os.path.join(models_dir, f"{asset}_max_up.json"))
    reg_down = xgb.XGBRegressor()
    reg_down.load_model(os.path.join(models_dir, f"{asset}_max_down.json"))
    
    df_astro = pd.read_parquet(MATRIX_FILE)
    df_astro["Date"] = pd.to_datetime(df_astro["Date"]).dt.tz_localize(None).astype("datetime64[us]")
    if "Close" in df_astro.columns: df_astro.drop(columns=["Close"], inplace=True)
    if "Volume" in df_astro.columns: df_astro.drop(columns=["Volume"], inplace=True)
    
    syn2 = syn.copy()
    syn2["Date"] = pd.to_datetime(syn2["dt"]).dt.tz_localize(None).astype("datetime64[us]")
    fused = pd.merge_asof(syn2.sort_values("Date"), df_astro.sort_values("Date"), on="Date", direction="backward")
    fused = fused.dropna(subset=["Tithi_Num"])
    
    with open(os.path.join(models_dir, "universal_feature_names.txt")) as f:
        cols = [l.strip() for l in f if l.strip()]
    
    X = fused[cols].fillna(0).values.astype(np.float32)
    pred_up   = reg_up.predict(X)
    pred_down = reg_down.predict(X)
    
    # Check if any MFE prediction is negative (CRITICAL)
    neg_mfe = (pred_up < 0).sum() + (pred_down < 0).sum()
    print(f"  {asset} max_up  pred: [{pred_up.min()*100:.3f}%, {pred_up.max()*100:.3f}%] | actual: [{max_ups.min()*100:.3f}%, {max_ups.max()*100:.3f}%]")
    print(f"  {asset} max_down pred: [{pred_down.min()*100:.3f}%, {pred_down.max()*100:.3f}%] | actual: [{max_downs.min()*100:.3f}%, {max_downs.max()*100:.3f}%]")
    print(f"  {asset} negative MFE/MAE predictions: {neg_mfe}")
    print()

# ── CHECK F: Dollar neutrality drift ─────────────────────────────────────
print("=== DOLLAR NEUTRALITY DRIFT CHECK ===")
assets_prices = {"COPX": 93.67, "NLR": 138.04, "XLV": 146.37, "SMH": 632.12, "XOP": 168.88, "KRE": 69.53}
spy_price = 759.47
CAPITAL = 10000.0
total_drift = 0
for a, p in assets_prices.items():
    asset_notional = int(CAPITAL / p) * p
    spy_notional   = int(CAPITAL / spy_price) * spy_price
    drift = abs(asset_notional - spy_notional)
    total_drift += drift
    print(f"  {a}: Asset leg=${asset_notional:.2f} | SPY leg=${spy_notional:.2f} | Unhedged=${drift:.2f}")
print(f"  TOTAL unhedged across all 6 sample trades: ${total_drift:.2f}")

# ── CHECK G: Weekend/after-hours resilience ───────────────────────────────
print()
print("=== TIMEZONE & TIMESTAMP RESILIENCE CHECK ===")
dummy_df = yf.download("SPY", period="1d", interval="1h", progress=False, auto_adjust=False)
dt_now = dummy_df.index[-1]
print(f"  SPY last bar: {dt_now} | tz={dt_now.tzinfo}")
try:
    dt_naive = dt_now.tz_localize(None)
    print(f"  tz_localize(None) on tz-AWARE timestamp: OK -> {dt_naive}")
except TypeError as e:
    print(f"  tz_localize(None) FAILED: {e}")
    # This is the bug path - already tz-naive
    print(f"  Should use tz_convert(None) instead")

print()
print("=== ALL CHECKS COMPLETE ===")
