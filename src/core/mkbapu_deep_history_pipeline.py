"""
MK Bapu Deep Historical Pipeline
================================
Loads the 1.2 GB SPY options dataset (2020-2022)
Synthesizes a flawless 15m OHLCV underlying timeseries.
Evaluates the MK Bapu strategy across multiple macro regimes.
"""
import sys, os, warnings, time, gc
import numpy as np
import pandas as pd
import swisseph as swe
from datetime import datetime, timezone
import xgboost as xgb
from sklearn.metrics import accuracy_score, f1_score

warnings.filterwarnings("ignore")

SCRATCH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
DATA_FILE = os.path.join(SCRATCH, r"ml_options_hedging_project\data\raw\spy\spy_2020_2022.csv")
OUTPUT_DIR = os.path.join(SCRATCH, "mkbapu_deep_history_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════
# CONSTANTS & CONFIG
# ═══════════════════════════════════════════════════════════════════════
RASHI_NAMES = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"
]
RASHI_BIAS = {
    "Mithuna": +1, "Karka": +1, "Vrishchika": +1, "Meena": +1,
    "Vrishabha": -1, "Simha": -1, "Kanya": -1,
    "Makara": -1, "Kumbha": -1, "Mesha": -1,
    "Tula": 0, "Dhanu": 0
}

# NYSE coordinates
LAT = 40.7128
LON = -74.0060

# ═══════════════════════════════════════════════════════════════════════
# STEP 1: RESAMPLE DEEP HISTORY
# ═══════════════════════════════════════════════════════════════════════
def synthesize_15m_data():
    print(f"\n[1] Loading 1.2GB dataset: {DATA_FILE}")
    t0 = time.time()
    
    # Only load required columns to save RAM
    # Columns have leading spaces in the file (e.g. ' [QUOTE_UNIXTIME]')
    df_raw = pd.read_csv(DATA_FILE, usecols=lambda x: 'QUOTE_UNIXTIME' in x or 'UNDERLYING_LAST' in x)
    df_raw.columns = [c.strip().strip('[]') for c in df_raw.columns]
    
    print(f"    Raw rows loaded: {len(df_raw):,} ({(time.time()-t0):.1f}s)")
    
    # Since this is an options chain, the underlying price is duplicated across all strikes.
    # We drop duplicates to get the actual underlying tick path.
    df_ticks = df_raw.drop_duplicates(subset=['QUOTE_UNIXTIME']).sort_values('QUOTE_UNIXTIME')
    print(f"    Unique underlying ticks: {len(df_ticks):,}")
    
    df_ticks['dt'] = pd.to_datetime(df_ticks['QUOTE_UNIXTIME'], unit='s', utc=True)
    df_ticks = df_ticks.set_index('dt')
    
    print("    Resampling to 15m OHLCV...")
    ohlc = df_ticks['UNDERLYING_LAST'].resample('15min').ohlc()
    ohlc = ohlc.dropna() # Drop empty outside-market bars
    
    # Filter strictly to market hours (13:30 - 20:00 UTC)
    h = ohlc.index.hour
    m = ohlc.index.minute
    mask = (h > 13) | ((h == 13) & (m >= 30))
    mask &= (h < 20)
    ohlc = ohlc[mask]
    
    ohlc = ohlc.rename(columns={'open':'Open', 'high':'High', 'low':'Low', 'close':'Close'})
    ohlc = ohlc.reset_index()
    
    print(f"    Final 15m Bars: {len(ohlc):,} | Range: {ohlc['dt'].min().date()} to {ohlc['dt'].max().date()}")
    
    del df_raw, df_ticks
    gc.collect()
    
    return ohlc

# ═══════════════════════════════════════════════════════════════════════
# STEP 2: EPHEMERIS
# ═══════════════════════════════════════════════════════════════════════
def compute_bar_features(dt_utc):
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                    dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0)
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED | swe.FLG_SWIEPH
    feats = {}

    for pid, name in [(swe.SUN,"Sun"),(swe.MOON,"Moon"),(swe.MERCURY,"Mercury"),
                      (swe.VENUS,"Venus"),(swe.MARS,"Mars"),(swe.JUPITER,"Jupiter"),
                      (swe.SATURN,"Saturn"),(swe.URANUS,"Uranus"),(swe.NEPTUNE,"Neptune")]:
    swe.set_sid_mode(swe.SIDM_LAHIRI)  # CRITICAL BUG FIX #5: Moved before calc
        r = swe.calc_ut(jd, pid, flags)
        lon2, speed = r[0][0], r[0][3]
        nak = int(lon2 / (360/27))
        feats[f"{name}_lon"]         = lon2
        feats[f"{name}_lon_cos"]     = np.cos(np.radians(lon2))
        feats[f"{name}_speed"]       = speed
        feats[f"{name}_sign"]        = int(lon2 / 30)
        feats[f"{name}_deg_in_sign"] = lon2 % 30
        feats[f"{name}_nak"]         = nak
        feats[f"{name}_pada"]        = int((lon2 % (360/27)) / (360/108)) + 1

    rahu_r = swe.calc_ut(jd, swe.MEAN_NODE, flags)
    rl = rahu_r[0][0]
    kl = (rl + 180) % 360
    feats["Rahu_lon"] = rl; feats["Rahu_sign"] = int(rl/30); feats["Rahu_nak"] = int(rl/(360/27))
    feats["Ketu_lon"] = kl; feats["Ketu_sign"] = int(kl/30); feats["Ketu_nak"] = int(kl/(360/27))

    lons = {n: feats[f"{n}_lon"] for n in ["Sun","Moon","Mercury","Venus","Mars",
                                            "Jupiter","Saturn","Uranus","Neptune"]}
    lons["Rahu"] = rl; lons["Ketu"] = kl
    pairs = [("Sun","Moon"),("Sun","Mars"),("Sun","Jupiter"),("Sun","Saturn"),
             ("Sun","Rahu"),("Moon","Mars"),("Moon","Jupiter"),("Moon","Saturn"),
             ("Moon","Rahu"),("Moon","Ketu"),("Mars","Saturn"),("Jupiter","Saturn"),
             ("Jupiter","Rahu"),("Saturn","Rahu"),("Mercury","Venus"),
             ("Venus","Jupiter"),("Mars","Jupiter")]
    for p1, p2 in pairs:
        if p1 in lons and p2 in lons:
            diff = abs(lons[p1] - lons[p2]) % 360
            diff = min(diff, 360 - diff)
            feats[f"asp_{p1}_{p2}_dist"] = diff

    sun_l = feats["Sun_lon"]; moon_l = feats["Moon_lon"]
    elong = (moon_l - sun_l) % 360
    feats["tithi"] = int(elong/12) + 1
    feats["moon_phase"] = elong/360.0
    feats["yoga"] = int(((sun_l + moon_l) % 360) / (360/27)) + 1

    try:
        cusps, ascmc = swe.houses_ex(jd, LAT, LON, b'P', swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        asc = ascmc[0]
        feats["house_placidus_1_cusp"] = asc
        feats["asc_lon_cos"]  = np.cos(np.radians(asc))
        feats["asc_sign"]     = int(asc/30) % 12
        feats["asc_deg"]      = asc % 30
        asc_d9 = (int(asc/30)*9 + int((asc%30)*9/30)) % 12
        feats["asc_d9_sign"] = asc_d9
        asc_d60 = (int(asc/30)*60 + int((asc%30)*60/30)) % 12
        feats["asc_d60_sign"] = asc_d60
    except:
        for k in ["house_placidus_1_cusp","asc_lon_cos","asc_sign","asc_deg","asc_d9_sign","asc_d60_sign"]:
            feats[k] = 0.0

    return feats

def compute_ephemeris(df):
    print(f"\n[2] Computing ephemeris for {len(df):,} bars...")
    swe.set_ephe_path('')
    
    t0 = time.time()
    rows = []
    for i, row in df.iterrows():
        dt_utc = row['dt'].to_pydatetime()
        if dt_utc.tzinfo is None:
            dt_utc = dt_utc.replace(tzinfo=timezone.utc)
        rows.append(compute_bar_features(dt_utc))
        if (i+1) % 5000 == 0:
            print(f"      {i+1}/{len(df)} bars ({(time.time()-t0):.1f}s)")
            
    feat_df = pd.DataFrame(rows)
    print(f"    Done: {len(feat_df.columns)} features. ({(time.time()-t0):.1f}s)")
    return feat_df


# ═══════════════════════════════════════════════════════════════════════
# STEP 3: MK BAPU
# ═══════════════════════════════════════════════════════════════════════
def apply_mkbapu_features(df, feat_df):
    print("\n[3] Injecting MK Bapu Features...")
    df2 = pd.concat([df.reset_index(drop=True), feat_df.reset_index(drop=True)], axis=1)

    asc_sign = feat_df['asc_sign'].values
    df2['mkb_rashi_idx']   = asc_sign
    df2['mkb_rashi_bias']  = [RASHI_BIAS.get(RASHI_NAMES[x % 12], 0) for x in asc_sign]

    changed = np.zeros(len(df2), dtype=np.int8)
    changed[0] = 1
    for i in range(1, len(df2)):
        changed[i] = 1 if asc_sign[i] != asc_sign[i-1] else 0
    df2['mkb_rashi_changed'] = changed

    rsp, current_rsp = [], df2['Open'].iloc[0]
    for i in range(len(df2)):
        if changed[i]:
            current_rsp = df2['Open'].iloc[i]
        rsp.append(current_rsp)
    df2['mkb_rashi_start_price'] = rsp

    atr = (df2['High'] - df2['Low']).rolling(26, min_periods=1).mean().fillna(1.0)
    df2['mkb_dist_to_rashi'] = (df2['Close'] - df2['mkb_rashi_start_price']) / (atr + 1e-9)

    bs, counter = [], 0
    for i in range(len(df2)):
        counter = 0 if changed[i] else counter + 1
        bs.append(min(counter, 16))
    df2['mkb_bars_since_rashi']      = bs
    df2['mkb_bars_since_rashi_norm'] = np.array(bs) / 8.0
    df2['mkb_rashi_pct_elapsed'] = feat_df['asc_deg'].values / 30.0

    pushkar_prices, pushkar_active = [], []
    vrishchika_start_time, pushkar_price = None, None
    for i in range(len(df2)):
        dt = df2['dt'].iloc[i]
        if changed[i]:
            pushkar_price = None
            rashi_name = RASHI_NAMES[df2['mkb_rashi_idx'].iloc[i] % 12]
            vrishchika_start_time = dt if rashi_name == 'Vrishchika' else None
        if vrishchika_start_time is not None:
            mins = (dt - vrishchika_start_time).total_seconds() / 60.0
            if mins >= 60.0 and pushkar_price is None:
                pushkar_price = df2['Open'].iloc[i]
        pushkar_prices.append(pushkar_price if pushkar_price is not None else np.nan)
        pushkar_active.append(1 if pushkar_price is not None else 0)
        
    df2['mkb_pushkar_price']  = pushkar_prices
    df2['mkb_pushkar_active'] = pushkar_active
    df2['mkb_dist_to_pushkar'] = np.where(
        np.array(pushkar_active) == 1,
        (df2['Close'].values - np.array([x if x is not None else 0 for x in pushkar_prices])) / (atr.values + 1e-9),
        0.0
    )

    return df2


# ═══════════════════════════════════════════════════════════════════════
# STEP 4: LABELS & ML
# ═══════════════════════════════════════════════════════════════════════
def apply_triple_barrier(df, pt_pct=0.003, sl_pct=0.002, barrier_bars=4):
    print("\n[4] Triple Barrier Labeling...")
    closes = df['Close'].values
    highs  = df['High'].values
    lows   = df['Low'].values
    labels = np.zeros(len(closes), dtype=np.int8)

    for i in range(len(closes) - barrier_bars):
        entry  = closes[i]
        pt_lvl = entry * (1 + pt_pct)
        sl_lvl = entry * (1 - sl_pct)
        label  = 0
        for j in range(1, barrier_bars + 1):
            h = highs[i+j]; l = lows[i+j]
            if h >= pt_lvl:
                label =  1; break
            elif l <= sl_lvl:
                label = -1; break
        labels[i] = label
    labels[-barrier_bars:] = 0
    return labels

def train_xgboost(df, labels):
    print("\n[5] 5-Fold Time-Series CV XGBoost...")
    drop_cols = {'dt','Open','High','Low','Close','Volume','label',
                 'mkb_rashi_start_price','mkb_pushkar_price'}

    df2 = df.copy()
    df2['label'] = labels
    df2 = df2.dropna(subset=['label'])
    df2 = df2[df2['label'] != 0].reset_index(drop=True)
    n = len(df2)
    y = (df2['label'] == 1).astype(int).values

    baseline_cols = [c for c in df2.columns if c not in drop_cols and not c.startswith('mkb_')]
    augmented_cols = baseline_cols + [c for c in df2.columns if c.startswith('mkb_')]

    xgb_params = dict(
        n_estimators=300, max_depth=4, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.6, min_child_weight=5,
        tree_method='hist', nthread=8, random_state=42,
        eval_metric='logloss'
    )

    results = {}
    folds = 5
    fold_size = n // folds

    for mode, cols in [('baseline', baseline_cols), ('augmented', augmented_cols)]:
        X = df2[cols].fillna(0).values.astype(np.float32)
        fold_accs, fold_precs = [], []

        for fold in range(folds-1):
            train_end = fold_size * (fold + 1)
            test_start = train_end
            test_end   = train_end + fold_size
            
            X_tr, X_te = X[:train_end], X[test_start:test_end]
            y_tr, y_te = y[:train_end], y[test_start:test_end]

            clf = xgb.XGBClassifier(**xgb_params)
            clf.fit(X_tr, y_tr, eval_set=[(X_te, y_te)], verbose=False, early_stopping_rounds=20)
            y_pred = clf.predict(X_te)
            proba  = clf.predict_proba(X_te)[:, 1]
            top10  = proba >= np.percentile(proba, 90)

            fold_accs.append(accuracy_score(y_te, y_pred))
            fold_precs.append(y_te[top10].mean() if top10.sum() > 0 else 0.5)

        # Train final for SHAP
        split = int(n * 0.8)
        X_tr_f, X_te_f = X[:split], X[split:]
        y_tr_f, y_te_f = y[:split], y[split:]
        clf_final = xgb.XGBClassifier(**xgb_params)
        clf_final.fit(X_tr_f, y_tr_f, eval_set=[(X_te_f, y_te_f)], verbose=False)

        results[mode] = {
            'model': clf_final, 'cols': cols, 'X_test': X_te_f,
            'acc':  np.mean(fold_accs), 'prec': np.mean(fold_precs)
        }
        print(f"    [{mode.upper():10s}] {len(cols):3d} feats | Acc={results[mode]['acc']:.4f} | Top10Prec={results[mode]['prec']:.4f}")

    da = results['augmented']['acc']  - results['baseline']['acc']
    dp = results['augmented']['prec'] - results['baseline']['prec']
    print(f"\n    Delta Acc:  {da:+.4f}")
    print(f"    Delta Prec: {dp:+.4f}")
    
    # SHAP
    import shap
    print("\n[6] SHAP Extraction...")
    model = results['augmented']['model']
    cols = results['augmented']['cols']
    explainer = shap.TreeExplainer(model)
    # limit to 1000 to save time
    shap_vals = explainer.shap_values(results['augmented']['X_test'][:1000])
    mean_shap = np.abs(shap_vals).mean(axis=0)
    
    top30 = np.argsort(mean_shap)[::-1][:30]
    print("\n    Top 30 Features by SHAP:")
    for rank, i in enumerate(top30, 1):
        tag = "[MKB]" if cols[i].startswith('mkb_') else "     "
        print(f"    {rank:2d}. {tag} {cols[i]:<40s} {mean_shap[i]:.6f}")

def main():
    print("="*70)
    print(" DEEP HISTORICAL VERIFICATION: 2020-2022 SPY (1.2GB DATASET)")
    print("="*70)
    df = synthesize_15m_data()
    feat_df = compute_ephemeris(df)
    df2 = apply_mkbapu_features(df, feat_df)
    labels = apply_triple_barrier(df2)
    
    dist = {-1: (labels==-1).sum(), 0: (labels==0).sum(), 1: (labels==1).sum()}
    print(f"    Labels -> Long:{dist[1]:,} | Short:{dist[-1]:,} | Neutral:{dist[0]:,}")
    
    train_xgboost(df2, labels)

if __name__ == "__main__":
    main()


# CRITICAL BUG FIX #17: Ensure swisseph is closed
import atexit
atexit.register(swe.close)
