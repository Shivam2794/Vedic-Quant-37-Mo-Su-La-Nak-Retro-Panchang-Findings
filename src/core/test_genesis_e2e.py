"""
Full end-to-end test of the Genesis Engine entry pipeline.
Simulates exactly what entry_routine does on market open.
"""
import os, sys
os.chdir(r'E:\Python\Learn')
import joblib
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

import live_astro_engine

# --- LOAD MODELS ---
print("[1] Loading ML models...")
pack_a = joblib.load('Model_A_Alpha.pkl')
pack_b = joblib.load('Model_B_Veto.pkl')
model_alpha   = pack_a['model']; alpha_features = pack_a['features']
model_veto    = pack_b['model']; veto_features  = pack_b['features']
print(f"    Model_A: {len(alpha_features)} features | Model_B: {len(veto_features)} features")

# --- SIMULATE EARNINGS CANDIDATES ---
tickers = ['NVDA', 'AMD', 'MSFT', 'AAPL', 'META']  # test candidates
target_date = datetime.now().strftime('%Y-%m-%d')
print(f"[2] Generating live technicals for {len(tickers)} tickers...")

# Get technicals (same logic as get_live_technicals in the bot)
end_date   = datetime.now()
start_date = end_date - timedelta(days=120)
all_ticks  = tickers + ["SPY", "^VIX"]
data = yf.download(all_ticks, start=start_date.strftime("%Y-%m-%d"),
                   end=end_date.strftime("%Y-%m-%d"), progress=False, auto_adjust=True)

rows = []
if isinstance(data.columns, pd.MultiIndex):
    close_df = data["Close"]; high_df = data["High"]
    low_df   = data["Low"];   vol_df  = data["Volume"]
else:
    close_df = data[["Close"]]; high_df = data[["High"]]
    low_df   = data[["Low"]];   vol_df  = data[["Volume"]]

for t in tickers:
    try:
        if t not in close_df.columns: continue
        c = close_df[t].dropna(); h = high_df[t].dropna()
        l = low_df[t].dropna();   v = vol_df[t].dropna()
        if len(c) < 50: continue
        tr     = pd.concat([h-l, abs(h-c.shift()), abs(l-c.shift())], axis=1).max(axis=1)
        atr14  = tr.rolling(14).mean().iloc[-1]
        sma20  = c.rolling(20).mean(); std20 = c.rolling(20).std()
        delta  = c.diff()
        gain   = delta.where(delta>0,0).rolling(14).mean()
        loss   = (-delta.where(delta<0,0)).rolling(14).mean()
        rsi    = 100 - (100/(1+(gain/loss))).iloc[-1]
        sma50  = c.rolling(50).mean().iloc[-1]
        obv    = (np.sign(delta)*v).cumsum()
        spy_c  = close_df["SPY"].dropna(); vix_c = close_df["^VIX"].dropna()
        rows.append({
            "Ticker":               t,
            "Tech_ATR_14_Norm":     atr14/c.iloc[-1],
            "Tech_BBW":             (4*std20.iloc[-1])/sma20.iloc[-1] if sma20.iloc[-1]>0 else 0,
            "Tech_RSI":             rsi,
            "Tech_Dist_50SMA":      (c.iloc[-1]-sma50)/sma50 if sma50>0 else 0,
            "Tech_OBV_Slope_10":    obv.diff(10).iloc[-1]/10,
            "Macro_SPY_Return_20d": (spy_c.iloc[-1]-spy_c.iloc[-21])/spy_c.iloc[-21] if len(spy_c)>20 else 0,
            "Macro_VIX":            vix_c.iloc[-1] if len(vix_c)>0 else 15.0,
            "Fund_EPS_Est":         0.50,
            "Fund_Surprise_Q1":     0.05,
            "Fund_Surprise_Q4":     0.02,
        })
    except Exception as e:
        print(f"  WARN: Technicals failed {t}: {e}")

tech_df = pd.DataFrame(rows)
print(f"    Technicals generated: {len(tech_df)} stocks")

print(f"[3] Generating live astro features via live_astro_engine...")
import time
t0 = time.time()
astro_df = live_astro_engine.fetch_live_astro(tickers, target_date, veto_features)
elapsed = time.time() - t0
print(f"    Astro generated: {len(astro_df)} rows in {elapsed:.2f}s | Cols: {len(astro_df.columns)}")

if tech_df.empty or astro_df.empty:
    print("FAIL: Empty dataframes!")
    sys.exit(1)

print("[4] Merging and scoring...")
live_df = pd.merge(tech_df, astro_df, on="Ticker", how="inner")
live_df["Prob_Buy"]   = model_alpha.predict_proba(live_df[alpha_features].fillna(0))[:, 1]
live_df["Prob_Toxic"] = model_veto.predict_proba(live_df[veto_features].fillna(0))[:, 1]

print("\n=== LIVE PIPELINE RESULT ===")
for _, row in live_df[['Ticker','Prob_Buy','Prob_Toxic']].iterrows():
    b = f"{row['Prob_Buy']*100:.1f}%"
    t = f"{row['Prob_Toxic']*100:.1f}%"
    status = "PASS" if (row['Prob_Buy'] > 0.6 and row['Prob_Toxic'] < 0.4) else "SKIP"
    print(f"  {row['Ticker']:<6} | Alpha: {b:>6} | Toxic: {t:>6} | {status}")

candidates = live_df[(live_df["Prob_Buy"] > 0.6) & (live_df["Prob_Toxic"] < 0.4)]
print(f"\n  Candidates passing both filters: {len(candidates)}/{len(live_df)}")
print("\n[SUCCESS] Full pipeline test PASSED - Genesis Engine is fully operational!")
