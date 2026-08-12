"""
DYNAMIC MASTER BACKTEST V2
==========================
Iteratively loads the individualized supreme matrix for each specific asset,
applies the XGBoost walk-forward algorithm, and runs the extreme noise gate.
"""

import os
import pandas as pd
import numpy as np
import yfinance as yf
from xgboost import XGBClassifier
from sklearn.model_selection import TimeSeriesSplit

BASE_DIR = r"C:\Users\patel\Desktop\Python\Learn"
ASSET_DIR = os.path.join(BASE_DIR, "asset_matrices_dual")

# The Ultimate 39-Asset Universe
UNIVERSE = [
    ("XME", "^GSPC", 12), ("USO", "^GSPC", 12), ("DBA", "^GSPC", 24), ("GDX", "^GSPC", 12),
    ("PPLT", "^GSPC", 12), ("XLC", "^GSPC", 12), ("XBI", "^GSPC", 12), ("EEM", "^GSPC", 6),
    ("QQQ", "^GSPC", 6), ("XLE", "^GSPC", 12), ("XLI", "^GSPC", 3), ("CPER", "^GSPC", 6),
    ("XLP", "^GSPC", 6), ("TAN", "^GSPC", 6), ("XLK", "^GSPC", 6), ("PAVE", "^GSPC", 3),
    ("UNG", "^GSPC", 12), ("HACK", "^GSPC", 6), ("IWM", "^GSPC", 6), ("DIA", "^GSPC", 6),
    ("HYG", "^GSPC", 6), ("XLU", "^GSPC", 6), ("ARKK", "^GSPC", 6), ("URA", "^GSPC", 3),
    ("XLV", "^GSPC", 6), ("XLRE", "^GSPC", 6), ("XOP", "^GSPC", 24), ("XLY", "^GSPC", 6),
    ("XLF", "^GSPC", 6), ("XLB", "^GSPC", 6), ("KRE", "^GSPC", 6), ("JETS", "^GSPC", 24),
    ("TLT", "^GSPC", 12), ("ITB", "^GSPC", 6),
    # Additional previously tested 
    ("GLD", "^GSPC", 24), ("SLV", "^GSPC", 24), ("SMH", "^GSPC", 6), ("NLR", "^GSPC", 24), ("COPX", "^GSPC", 6)
]

def load_price_data(ticker):
    file_path = os.path.join(BASE_DIR, f"{ticker}_daily.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, parse_dates=["Date"])
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        return df
    else:
        print(f"Downloading {ticker}...")
        tkr = yf.Ticker(ticker)
        df = tkr.history(start="2005-01-01", end="2026-12-31", auto_adjust=False)
        df.reset_index(inplace=True)
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        df.to_csv(file_path, index=False)
        return df

def clean_wfo(df_model):
    drop_cols = ["Date", "Target_Fwd", "Return_Fwd", "Ticker", "Open", "High", "Low", "Close", "Volume", "Dividends", "Stock Splits"]
    features = [c for c in df_model.columns if c not in drop_cols]
    X = df_model[features]
    y = df_model["Target_Fwd"]
    returns = df_model["Return_Fwd"]
    
    tscv = TimeSeriesSplit(n_splits=5)
    xgb = XGBClassifier(
        n_estimators=100, max_depth=3, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8,
        random_state=42, n_jobs=-1
    )
    
    all_trades = []
    seen_dates = set()
    
    for train_idx, test_idx in tscv.split(X):
        X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
        X_test, y_test = X.iloc[test_idx], y.iloc[test_idx]
        ret_test = returns.iloc[test_idx]
        dates_test = df_model["Date"].iloc[test_idx]
        
        xgb.fit(X_train, y_train)
        preds = xgb.predict(X_test)
        
        for p, r, d in zip(preds, ret_test, dates_test):
            if p == 1 and d not in seen_dates:
                all_trades.append(r)
                seen_dates.add(d)
                
    if not all_trades: return 0, 0, 0, 0
    c_ret = np.cumsum(all_trades)
    cagr = c_ret[-1]
    mdd = np.min(c_ret - np.maximum.accumulate(c_ret)) if len(c_ret) > 0 else 0
    calmar = cagr / abs(mdd) if mdd != 0 else 0
    win_rate = len([x for x in all_trades if x > 0]) / len(all_trades)
    return cagr, mdd, calmar, win_rate

def test_noise(df_model):
    df_noise = df_model.copy()
    drop_cols = ["Date", "Target_Fwd", "Return_Fwd", "Ticker", "Open", "High", "Low", "Close", "Volume", "Dividends", "Stock Splits"]
    features = [c for c in df_model.columns if c not in drop_cols]
    # Destroy intelligence by shuffling each column
    for f in features:
        df_noise[f] = np.random.permutation(df_noise[f].values)
    return clean_wfo(df_noise)

results = []
print("="*100)
print(f" DYNAMIC MASTER QUALITY REPORT — Testing 39 Individualized Asset Matrices")
print("="*100)
print(f"{'ASSET':<10} {'CAGR':>8} {'MDD':>8} {'CALMAR':>8} {'WR':>6} {'NOISE Δ':>10} {'BAR VERDICT':<22}")
print("-" * 100)

for ticker, bench, barrier_h in UNIVERSE:
    matrix_file = os.path.join(ASSET_DIR, f"{ticker}_matrix.parquet")
    if not os.path.exists(matrix_file):
        print(f"{ticker:<10} MATRIX NOT FOUND ❌")
        continue
        
    df_astro = pd.read_parquet(matrix_file)
    df_astro["Date"] = pd.to_datetime(df_astro["Date"])
    
    df_price = load_price_data(ticker)
    df_price["Date"] = pd.to_datetime(df_price["Date"])
    
    df = pd.merge(df_price, df_astro, on="Date", how="inner")
    if len(df) < 500:
        print(f"{ticker:<10} INSUFFICIENT HISTORY ❌")
        continue
        
    # Standard Forward target
    df["Return_Fwd"] = df["Close"].pct_change(barrier_h).shift(-barrier_h)
    df["Target_Fwd"] = (df["Return_Fwd"] > 0).astype(int)
    df.dropna(inplace=True)
    
    cagr, mdd, calmar, wr = clean_wfo(df)
    n_cagr, n_mdd, n_calmar, n_wr = test_noise(df)
    
    noise_delta = cagr - n_cagr
    
    verdict = ""
    if noise_delta <= 0: verdict = "NOISE FAIL ❌"
    elif cagr < 0.15: verdict = "CAGR LOW ❌"
    elif mdd < -0.60: verdict = "MDD FAIL ❌"
    elif calmar < 0.35: verdict = "CALMAR LOW ❌"
    elif wr < 0.51: verdict = "WR LOW ❌"
    else: verdict = "PASS ✅"
    
    results.append({
        "Asset": ticker, "CAGR": cagr, "MDD": mdd, "Calmar": calmar,
        "WR": wr, "Noise_Delta": noise_delta, "Verdict": verdict
    })
    
    print(f"{ticker:<10} {cagr*100:>7.1f}% {mdd*100:>7.1f}% {calmar:>7.2f}x {wr*100:>5.1f}% {noise_delta*100:>9.1f}%  {verdict}")

print("\n==================================================")
passes = [r for r in results if "PASS" in r["Verdict"]]
print(f" DYNAMIC ARCHITECTURE RESULT: {len(passes)} assets cleared ALL gates")
print("==================================================")
for p in passes:
    print(f"  ✅ {p['Asset']:<5} CAGR={p['CAGR']*100:+.1f}%  MDD={p['MDD']*100:.1f}%  Calmar={p['Calmar']:+.2f}x  NoiseΔ={p['Noise_Delta']*100:+.1f}%")
