import sys, warnings
import numpy as np
import pandas as pd
import swisseph as swe
import yfinance as yf
from datetime import datetime, timezone
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit

warnings.filterwarnings("ignore")
PAIRS = {'SMH_SPY': ('SMH', 'SPY', 'US', 40.7128, -74.0060)}
BARRIER_BARS, PT_MULT, SL_MULT = 6, 1.5, 1.0

def fetch_pair_data(asset, benchmark, market):
    df_asset = yf.download(asset, period="730d", interval="1h", progress=False, auto_adjust=False)
    df_bench = yf.download(benchmark, period="730d", interval="1h", progress=False, auto_adjust=False)
    if isinstance(df_asset.columns, pd.MultiIndex): df_asset.columns = df_asset.columns.get_level_values(0)
    if isinstance(df_bench.columns, pd.MultiIndex): df_bench.columns = df_bench.columns.get_level_values(0)
    df_asset = df_asset[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
    df_bench = df_bench[['Open', 'High', 'Low', 'Close']].dropna()
    df, bench = df_asset.align(df_bench, join='inner', axis=0)
    syn = pd.DataFrame()
    syn['Open'] = df['Open'] / bench['Open']
    syn['High'] = df['High'] / bench['High']
    syn['Low'] = df['Low'] / bench['Low']
    syn['Close'] = df['Close'] / bench['Close']
    syn['Volume'] = df['Volume']
    syn['dt'] = syn.index
    mask = (syn.index.hour >= 9) & (syn.index.hour <= 15)
    return syn[mask].reset_index(drop=True)

def compute_ephemeris(df, lat, lon):
    swe.set_ephe_path('')
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    rows = []
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED | swe.FLG_SWIEPH
    for i, row in df.iterrows():
        dt_utc = row['dt'].to_pydatetime()
        if dt_utc.tzinfo is not None: dt_utc = dt_utc.astimezone(timezone.utc).replace(tzinfo=None)
        jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60.0)
        feats = {}
        for pid, name in [(swe.SUN,"Sun"),(swe.MOON,"Moon"),(swe.MERCURY,"Mercury"),(swe.VENUS,"Venus"),(swe.MARS,"Mars"),(swe.JUPITER,"Jupiter"),(swe.SATURN,"Saturn"),(swe.URANUS,"Uranus"),(swe.NEPTUNE,"Neptune")]:
            r = swe.calc_ut(jd, pid, flags)
            lon2 = r[0][0]
            feats[f"{name}_lon_cos"], feats[f"{name}_lon_sin"] = np.cos(np.radians(lon2)), np.sin(np.radians(lon2))
            feats[f"{name}_sign"] = int(lon2 / 30)
        try:
            cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
            asc = ascmc[0]
            feats["house_placidus_1_cusp"] = asc
            feats["asc_lon_cos"], feats["asc_lon_sin"] = np.cos(np.radians(asc)), np.sin(np.radians(asc))
            feats["asc_sign"], feats["asc_deg"] = int(asc/30) % 12, asc % 30
            feats["asc_d60_sign"] = (int(asc/30)*60 + int((asc%30)*60/30)) % 12
        except:
            for k in ["house_placidus_1_cusp","asc_lon_cos","asc_lon_sin","asc_sign","asc_deg","asc_d60_sign"]: feats[k] = 0.0
        rows.append(feats)
    return pd.DataFrame(rows)

def apply_features(df, feat_df):
    df2 = pd.concat([df.reset_index(drop=True), feat_df.reset_index(drop=True)], axis=1)
    asc_sign = feat_df['asc_sign'].values
    changed = np.zeros(len(df2), dtype=np.int8)
    changed[0] = 1
    for i in range(1, len(df2)): changed[i] = 1 if asc_sign[i] != asc_sign[i-1] else 0
    rsp, current_rsp = [], df2['Open'].iloc[0]
    for i in range(len(df2)):
        if changed[i]: current_rsp = df2['Open'].iloc[i]
        rsp.append(current_rsp)
    df2['mkb_rashi_start_price'] = rsp
    df2['mkb_atr'] = (df2['High'] - df2['Low']).rolling(14, min_periods=1).mean().fillna(df2['Close']*0.001)
    df2['mkb_dist_to_rashi'] = (df2['Close'] - df2['mkb_rashi_start_price']) / (df2['mkb_atr'] + 1e-9)
    return df2

def apply_labels(df):
    closes, highs, lows, atrs = df['Close'].values, df['High'].values, df['Low'].values, df['mkb_atr'].values
    n = len(closes)
    ll, sl = np.zeros(n, dtype=np.int8), np.zeros(n, dtype=np.int8)
    for i in range(n - BARRIER_BARS):
        entry, atr = closes[i], atrs[i]
        pt_l, sl_l = entry + (PT_MULT * atr), entry - (SL_MULT * atr)
        pt_s, sl_s = entry - (PT_MULT * atr), entry + (SL_MULT * atr)
        for j in range(1, BARRIER_BARS + 1):
            if lows[i+j] <= sl_l: break
            if highs[i+j] >= pt_l: ll[i] = 1; break
        for j in range(1, BARRIER_BARS + 1):
            if highs[i+j] >= sl_s: break
            if lows[i+j] <= pt_s: sl[i] = 1; break
    df['label_long'], df['label_short'] = ll, sl
    return df

def execute_wfo_proof(df):
    df2 = apply_labels(df).iloc[:-BARRIER_BARS].reset_index(drop=True)
    cols = [c for c in df2.columns if c.endswith('_cos') or c.endswith('_sin') or c.endswith('_sign') or c.endswith('_deg') or c.startswith('mkb_dist')]
    X = df2[cols].fillna(0).values.astype(np.float32)
    y_l, y_s = df2['label_long'].values, df2['label_short'].values
    m_raw = np.column_stack([df2['mkb_atr'].values, df2['Volume'].values])
    closes, highs, lows, atrs = df2['Close'].values, df2['High'].values, df2['Low'].values, df2['mkb_atr'].values
    
    xgb_params = dict(n_estimators=100, max_depth=3, learning_rate=0.05, tree_method='hist', random_state=42)
    tscv = TimeSeriesSplit(n_splits=5)
    
    long_rets, short_rets = [], []
    
    for tr, te in tscv.split(X):
        # Long
        m_l = xgb.XGBClassifier(**xgb_params)
        if len(np.unique(y_l[tr]))>1: m_l.fit(X[tr], y_l[tr], verbose=False)
        else: m_l.fit(np.vstack([X[tr], np.zeros_like(X[tr][0])]), np.append(y_l[tr], 1-y_l[tr][0]), verbose=False)
        # Short
        m_s = xgb.XGBClassifier(**xgb_params)
        if len(np.unique(y_s[tr]))>1: m_s.fit(X[tr], y_s[tr], verbose=False)
        else: m_s.fit(np.vstack([X[tr], np.zeros_like(X[tr][0])]), np.append(y_s[tr], 1-y_s[tr][0]), verbose=False)
        
        preds_l, preds_s = m_l.predict(X[te]), m_s.predict(X[te])
        
        for i, idx in enumerate(te):
            if idx >= len(closes) - BARRIER_BARS: continue
            
            # Simple proof without Meta-Model complex veto just to see Raw Long vs Raw Short capability
            signal = 0
            if preds_l[i] == 1: signal = 1
            elif preds_s[i] == 1: signal = -1
            if signal == 0: continue
            
            entry, atr = closes[idx], atrs[idx]
            pt, sl_amt = PT_MULT * atr, SL_MULT * atr
            trade_ret = 0.0
            
            if signal == 1:
                for j in range(1, BARRIER_BARS + 1):
                    if lows[idx+j] <= entry - sl_amt: trade_ret = -sl_amt/entry; break
                    if highs[idx+j] >= entry + pt: trade_ret = pt/entry; break
                if trade_ret == 0.0: trade_ret = (closes[idx+BARRIER_BARS] - entry) / entry
                long_rets.append(trade_ret)
            else:
                for j in range(1, BARRIER_BARS + 1):
                    if highs[idx+j] >= entry + sl_amt: trade_ret = -sl_amt/entry; break
                    if lows[idx+j] <= entry - pt: trade_ret = pt/entry; break
                if trade_ret == 0.0: trade_ret = (entry - closes[idx+BARRIER_BARS]) / entry
                short_rets.append(trade_ret)

    lr, sr = np.array(long_rets), np.array(short_rets)
    print("=== SMH/SPY LONG VS SHORT PROOF ===")
    print(f"Total Longs: {len(lr)}")
    if len(lr)>0:
        pf_l = abs(lr[lr>0].sum() / lr[lr<0].sum()) if lr[lr<0].sum() != 0 else np.inf
        print(f"Long Win Rate: {(lr>0).mean()*100:.1f}% | Long PF: {pf_l:.2f}")
    
    print(f"\nTotal Shorts: {len(sr)}")
    if len(sr)>0:
        pf_s = abs(sr[sr>0].sum() / sr[sr<0].sum()) if sr[sr<0].sum() != 0 else np.inf
        print(f"Short Win Rate: {(sr>0).mean()*100:.1f}% | Short PF: {pf_s:.2f}")

try:
    d = fetch_pair_data('SMH', 'SPY', 'US')
    f = compute_ephemeris(d, 40.7128, -74.0060)
    d2 = apply_features(d, f)
    execute_wfo_proof(d2)
except Exception as e:
    print(e)


# CRITICAL BUG FIX #17: Ensure swisseph is closed
import atexit
atexit.register(swe.close)
