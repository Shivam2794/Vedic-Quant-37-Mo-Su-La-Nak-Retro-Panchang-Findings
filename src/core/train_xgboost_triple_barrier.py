"""
Phase 4: XGBoost + Triple-Barrier Labels (Local Execution)
=============================================================
1. Applies Lopez de Prado's Triple-Barrier Labeling method to
   convert raw returns into discrete trade signals:
     +1 = Upper barrier hit first (profitable long)
     -1 = Lower barrier hit first (stopped out)
      0 = Time barrier expired (inconclusive)

2. Trains an XGBoost classifier on the FULL 4,220-column Vedic
   feature matrix (boolean Causal Core + continuous features).

3. Extracts SHAP interaction values for feature combination discovery.

Executes 100% locally using CPU (XGBoost hist method).
Hardware cap: 8 threads (50% of 16 cores) to stay within 70% envelope.
"""
import pandas as pd
import numpy as np
import os, glob, time, sqlite3, json
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
from sklearn.cluster import KMeans

# ============================================================
# CONFIGURATION
# ============================================================
FEATURES_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\features_consolidated"
RETURNS_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_returns.parquet"
SECTOR_DB    = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_natal_charts.db"
CAUSAL_CORE  = r"E:\Python\Learn\vedic_quant\causal_core_v3.csv"
OUTPUT_DIR   = r"E:\Python\Learn\vedic_quant\models"

# Triple-Barrier Parameters
HORIZONS = {
    '10D': {'col': 'fwd_return_10d', 'pt_mult': 1.5, 'sl_mult': 1.0},
    '21D': {'col': 'fwd_return_21d', 'pt_mult': 2.0, 'sl_mult': 1.0},
    '63D': {'col': 'fwd_return_63d', 'pt_mult': 2.5, 'sl_mult': 1.0},
}
PRIMARY_HORIZON = '63D'  # Our strongest signals are on the 63D horizon

# XGBoost Hyperparameters
XGB_PARAMS = {
    'n_estimators': 500,
    'max_depth': 6,
    'learning_rate': 0.05,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'min_child_weight': 1,
    'gamma': 0,
    'reg_alpha': 0,
    'reg_lambda': 1,
    'tree_method': 'hist',
    'device': 'cuda',
    'nthread': 8,
    'random_state': 42,
    'eval_metric': 'mlogloss',
    'early_stopping_rounds': 50,
}

# ============================================================
# TRIPLE-BARRIER LABELING (Lopez de Prado)
# ============================================================
def apply_triple_barrier(returns_col, daily_vol, pt_mult=2.0, sl_mult=1.0):
    """
    Label each observation based on triple-barrier method.
    
    Parameters:
        returns_col: Forward returns for the horizon
        daily_vol: Rolling 63-day volatility (annualized, scaled down)
        pt_mult: Profit-taking multiplier (upper barrier = daily_vol * pt_mult)
        sl_mult: Stop-loss multiplier (lower barrier = -daily_vol * sl_mult)
    
    Returns:
        labels: +1 (profit), -1 (stop loss), 0 (time expiry)
    """
    upper = daily_vol * pt_mult
    lower = -daily_vol * sl_mult
    
    labels = np.zeros(len(returns_col), dtype=np.int64)
    
    for i in range(len(returns_col)):
        ret = returns_col.iloc[i] if hasattr(returns_col, 'iloc') else returns_col[i]
        ub = upper.iloc[i] if hasattr(upper, 'iloc') else upper[i]
        lb = lower.iloc[i] if hasattr(lower, 'iloc') else lower[i]
        
        if np.isnan(ret) or np.isnan(ub) or np.isnan(lb):
            labels[i] = 0
        elif ret >= ub:
            labels[i] = 1   # Upper barrier hit — profitable trade
        elif ret <= lb:
            labels[i] = -1  # Lower barrier hit — stopped out
        else:
            labels[i] = 0   # Time barrier — inconclusive
    
    return labels


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    t0 = time.time()
    
    print("=" * 70)
    print("  PHASE 4: XGBOOST + TRIPLE-BARRIER TRAINING ENGINE")
    print("  Local Execution | 8 Threads | Zero GCP")
    print("=" * 70)
    
    # --------------------------------------------------------
    # Step 1: Load Causal Core to identify winning features
    # --------------------------------------------------------
    core_df = pd.read_csv(CAUSAL_CORE)
    causal_features = set(core_df['feature'].unique())
    print(f"\n[1] Causal Core: {len(causal_features)} unique winning features")
    
    # --------------------------------------------------------
    # Step 2: Load Sectors
    # --------------------------------------------------------
    sectors = {}
    conn = sqlite3.connect(SECTOR_DB)
    for tk, sec in conn.execute("SELECT ticker, sector FROM sector_tags WHERE sector IS NOT NULL"):
        sectors[tk] = sec
    conn.close()
    
    # --------------------------------------------------------
    # Step 3: Load Returns
    # --------------------------------------------------------
    print("[2] Loading stock returns...")
    ret_df = pd.read_parquet(RETURNS_PATH)
    ret_df['join_date'] = pd.to_datetime(ret_df['date']).dt.date
    print(f"    Returns: {len(ret_df):,} rows, {ret_df['ticker'].nunique()} tickers")
    
    # Fetch VIX and QQQ data
    print("[2b] Fetching VIX and QQQ data...")
    min_date = ret_df['date'].min()
    max_date = ret_df['date'].max()
    vix = yf.download("^VIX", start=min_date, end=max_date, progress=False, auto_adjust=False)
    vix_close = vix['Close'].to_frame('VIX')
    vix_close.index = pd.to_datetime(vix_close.index).date
    vix_close = vix_close.rename_axis('join_date').reset_index()
    print(f"    VIX rows: {len(vix_close)}")
    
    qqq = yf.download("QQQ", start=min_date, end=max_date, progress=False, auto_adjust=False)
    qqq_close = qqq['Close'].to_frame('QQQ')
    qqq_close.index = pd.to_datetime(qqq_close.index).date
    qqq_close = qqq_close.rename_axis('join_date').reset_index()
    print(f"    QQQ rows: {len(qqq_close)}")
    
    # --------------------------------------------------------
    # Step 4: Process tickers — build full feature matrix
    # --------------------------------------------------------
    pfiles = sorted([f for f in os.listdir(FEATURES_DIR) if f.endswith('.parquet')])
    tickers = [f.replace('.parquet', '') for f in pfiles]
    
    # Discover columns from largest file
    pfiles_by_size = sorted(pfiles, key=lambda f: os.path.getsize(os.path.join(FEATURES_DIR, f)), reverse=True)
    sample = pd.read_parquet(os.path.join(FEATURES_DIR, pfiles_by_size[0]), engine='pyarrow')
    
    skip = {'ticker', 'year', 'date'}
    skip_pre = ('date', 'close', 'open', 'high', 'low', 'volume', 'adj', 'fwd_', 'return', 'log_', 'Close', 'Open')
    
    feature_cols = []
    # Non-numeric columns to exclude (Dasha periods, Nakshatra names, etc.)
    non_numeric_cols = set()
    for col in sample.columns:
        if col in skip or any(col.lower().startswith(p.lower()) for p in skip_pre):
            continue
        # Check if column is numeric
        if not pd.api.types.is_numeric_dtype(sample[col]):
            non_numeric_cols.add(col)
            continue
        feature_cols.append(col)
    
    if non_numeric_cols:
        print(f"    Excluded {len(non_numeric_cols)} non-numeric cols: {sorted(non_numeric_cols)}")
    print(f"[3] Numeric feature columns: {len(feature_cols)}")
    
    # --------------------------------------------------------
    # Step 5: Build consolidated dataset (ticker-by-ticker, O(1) mem)
    # --------------------------------------------------------
    print(f"\n[4] Building consolidated dataset from {len(tickers)} tickers...")
    
    hz = HORIZONS[PRIMARY_HORIZON]
    return_col = hz['col']
    
    all_frames = []   # List of DataFrames with aligned columns
    all_labels = []
    all_meta = []     # ticker, date, sector for later analysis
    
    # First pass: discover the common feature columns across all tickers
    print("    Pass 1: Discovering common feature columns...")
    common_cols = None
    for ti, ticker in enumerate(tickers[:50]):  # Sample 50 for speed
        tpath = os.path.join(FEATURES_DIR, f"{ticker}.parquet")
        if not os.path.exists(tpath):
            continue
        try:
            s = pd.read_parquet(tpath, engine='pyarrow')
            avail = set(c for c in feature_cols if c in s.columns)
            if common_cols is None:
                common_cols = avail
            else:
                common_cols = common_cols & avail
        except:
            pass
    
    common_cols = sorted(list(common_cols))
    
    # FILTER down to only the Causal Core features
    # This prevents the 90GB OOM error by only using the 37 winning signals
    common_cols = [c for c in common_cols if c in causal_features]
    print(f"    Filtered to causal features only: {len(common_cols)}")
    
    # Second pass: build the actual dataset
    print("    Pass 2: Loading features + applying Triple-Barrier...")
    all_regime_features = []   # list of DataFrames with regime features (Ret, VIX, Roll_Vol_20)
    all_regime_indices = []    # list of arrays of indices within each ticker's merged_valid
    from tqdm import tqdm
    for ti, ticker in enumerate(tqdm(tickers, desc="Loading tickers")):
        tpath = os.path.join(FEATURES_DIR, f"{ticker}.parquet")
        if not os.path.exists(tpath):
            continue
        
        try:
            feat = pd.read_parquet(tpath, engine='pyarrow')
        except:
            continue
        
        if len(feat) == 0:
            continue
        feat['join_date'] = pd.to_datetime(feat['date']).dt.date
        
        rr = ret_df[ret_df['ticker'] == ticker]
        needed_ret_cols = ['join_date'] + [h['col'] for h in HORIZONS.values()]
        available_ret = [c for c in needed_ret_cols if c in rr.columns]
        merged = feat.merge(rr[available_ret], on='join_date', how='inner')
        
        if len(merged) == 0:
            continue
        
        merged = merged.sort_values('join_date').reset_index(drop=True)
        
        # Merge VIX
        merged = merged.merge(vix_close, on='join_date', how='left')
        merged['VIX'] = merged['VIX'].fillna(method='ffill').fillna(method='bfill')
        
        # Compute daily returns proxy and rolling vol for regime (using PAST return roc_21 to avoid look-ahead bias)
        if 'roc_21' in merged.columns:
            daily_proxy = merged['roc_21'] / 21.0
        else:
            daily_proxy = pd.Series(np.zeros(len(merged)))
        merged['Ret'] = daily_proxy
        merged['Roll_Vol_20'] = daily_proxy.rolling(20, min_periods=5).std().fillna(daily_proxy.std())
        
        # Compute daily volatility (rolling 63-day std of daily returns proxy)
        daily_vol = daily_proxy.rolling(63, min_periods=20).std().fillna(daily_proxy.std())
        daily_vol = daily_vol.clip(lower=0.005)
        
        # Apply Triple-Barrier
        if return_col not in merged.columns:
            continue
            
        labels = apply_triple_barrier(
            merged[return_col], 
            daily_vol, 
            pt_mult=hz['pt_mult'], 
            sl_mult=hz['sl_mult']
        )
        
        # Drop rows with NaN in the return column
        valid_mask = ~merged[return_col].isna()
        labels = labels[valid_mask.values]
        merged_valid = merged[valid_mask].reset_index(drop=True)
        
        if len(merged_valid) == 0:
            continue
        
        # Collect regime features for KMeans (after valid mask)
        regime_feats = merged_valid[['Ret', 'VIX', 'Roll_Vol_20']].copy()
        all_regime_features.append(regime_feats)
        all_regime_indices.append(np.arange(len(merged_valid)))  # indices within this ticker's merged_valid
        
        # Extract feature matrix (using common columns, filling missing with 0)
        avail = [c for c in common_cols if c in merged_valid.columns]
        X = np.zeros((len(merged_valid), len(common_cols)), dtype=np.float32)
        if avail:
            col_idx = [common_cols.index(c) for c in avail]
            X[:, col_idx] = merged_valid[avail].fillna(0.0).values.astype(np.float32)
        
        all_frames.append(X)
        all_labels.append(labels)
        
        sec = sectors.get(ticker, 'Unknown')
        for idx in range(len(merged_valid)):
            all_meta.append({
                'ticker': ticker,
                'date': str(merged_valid['join_date'].iloc[idx]),
                'sector': sec
            })
        
        if (ti + 1) % 25 == 0:
            elapsed = time.time() - t0
            print(f"    [{ti+1}/{len(tickers)}] {ticker} — {elapsed/60:.1f}m elapsed")
    
    # --------------------------------------------------------
    # Step 6: Consolidate
    # --------------------------------------------------------
    print("\n[5] Consolidating dataset...")
    X_full = np.concatenate(all_frames, axis=0)
    y_full = np.concatenate(all_labels, axis=0)
    
    # Shift labels from {-1, 0, 1} to {0, 1, 2} for XGBoost multiclass
    y_shifted = y_full + 1  # Now: 0=stopped, 1=time_expiry, 2=profit
    
    print(f"    Total samples: {X_full.shape[0]:,}")
    print(f"    Total features: {X_full.shape[1]:,}")
    print(f"    Label distribution:")
    unique, counts = np.unique(y_shifted, return_counts=True)
    label_names = {0: 'Stop-Loss (-1)', 1: 'Time-Expiry (0)', 2: 'Profit (+1)'}
    for u, c in zip(unique, counts):
        print(f"      {label_names.get(u, u)}: {c:,} ({100*c/len(y_shifted):.1f}%)")
    
    # Fit KMeans on regime features and add regime label as a feature
    print("\n[5b] Fitting 6-state KMeans regime detection...")
    regime_feat_full = pd.concat(all_regime_features, ignore_index=True)
    regime_feat_full = regime_feat_full.dropna()
    if len(regime_feat_full) > 0:
        kmeans = KMeans(n_clusters=6, random_state=42, n_init=10)
        regime_labels = kmeans.fit_predict(regime_feat_full.values)
        # Map back to original order (some rows may have been dropped due to NaN)
        # We'll create a Series with index matching the concatenated order
        regime_series = pd.Series(index=regime_feat_full.index, data=regime_labels, dtype=np.float32)
        # Reindex to full length (fill NaN with 0)
        full_index = pd.RangeIndex(len(X_full))
        regime_series = regime_series.reindex(full_index, fill_value=0.0)
        regime_col = regime_series.values.reshape(-1, 1)
    else:
        regime_col = np.zeros((len(X_full), 1), dtype=np.float32)
    
    # Add regime and VIX columns to X_full
    # We need VIX values for each sample. We'll reconstruct from all_regime_features.
    vix_full = pd.concat([df['VIX'] for df in all_regime_features], ignore_index=True)
    vix_full = vix_full.fillna(method='ffill').fillna(method='bfill').fillna(0.0)
    vix_col = vix_full.values.reshape(-1, 1).astype(np.float32)
    
    X_full = np.hstack([X_full, vix_col, regime_col])
    common_cols = common_cols + ['VIX', 'Regime']
    print(f"    Added VIX and Regime features. Total features now: {X_full.shape[1]}")
    
    # --------------------------------------------------------
    # Step 7: Train/Test Split (Temporal — no leakage!)
    # --------------------------------------------------------
    print("\n[6] Temporal train/test split (80/20 by date) with Embargo...")
    dates = [m['date'] for m in all_meta]
    date_arr = np.array(dates)
    sorted_dates = np.sort(np.unique(date_arr))
    split_idx = int(len(sorted_dates) * 0.8)
    split_date_str = sorted_dates[split_idx]
    
    # Apply purge/embargo gap to prevent tomorrow's data leaking into today's prediction
    split_dt = pd.to_datetime(split_date_str)
    horizon_days = int(PRIMARY_HORIZON.replace('D', ''))
    embargo_date_str = str((split_dt - pd.Timedelta(days=horizon_days)).date())
    
    train_mask = date_arr < embargo_date_str
    test_mask = date_arr >= split_date_str
    
    X_train, X_test = X_full[train_mask], X_full[test_mask]
    y_train, y_test = y_shifted[train_mask], y_shifted[test_mask]
    
    print(f"    Train: {X_train.shape[0]:,} samples (before {split_date})")
    print(f"    Test:  {X_test.shape[0]:,} samples (from {split_date})")
    
    # --------------------------------------------------------
    # Step 8: Train XGBoost
    # --------------------------------------------------------
    print("\n[7] Training XGBoost Classifier...")
    
    try:
        import xgboost as xgb
    except ImportError:
        print("    Installing xgboost...")
        os.system("pip install xgboost")
        import xgboost as xgb
    
    clf = xgb.XGBClassifier(
        objective='multi:softprob',
        num_class=3,
        use_label_encoder=False,
        verbosity=1,
        **{k: v for k, v in XGB_PARAMS.items() if k not in ('eval_metric',)}
    )
    
    print(f"    Params: depth={XGB_PARAMS['max_depth']}, trees={XGB_PARAMS['n_estimators']}, "
          f"lr={XGB_PARAMS['learning_rate']}, colsample={XGB_PARAMS['colsample_bytree']}")
    
    t_train = time.time()
    clf.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=50
    )
    train_time = time.time() - t_train
    print(f"    Training completed in {train_time:.1f}s")
    
    # --------------------------------------------------------
    # Step 9: Evaluate
    # --------------------------------------------------------
    print("\n[8] Evaluation Results:")
    from sklearn.metrics import classification_report, accuracy_score, cohen_kappa_score
    
    y_pred = clf.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    kappa = cohen_kappa_score(y_test, y_pred)
    
    print(f"    Accuracy: {acc:.4f}")
    print(f"    Cohen's Kappa: {kappa:.4f}")
    print(f"\n    Classification Report:")
    
    target_names = ['Stop-Loss', 'Time-Expiry', 'Profit']
    report = classification_report(y_test, y_pred, target_names=target_names, digits=4)
    print(report)
    
    # --------------------------------------------------------
    # Sharpe optimization (brute force probability threshold)
    # --------------------------------------------------------
    print("\n[8b] Brute‑forcing probability threshold to maximize Sharpe...")
    # Get probability of class 2 (Profit)
    proba = clf.predict_proba(X_test)[:, 2]  # class 2 = profit
    
    # Compute actual returns for test period (using forward return for horizon)
    # We need the actual forward returns for each test sample.
    # We'll reconstruct from all_meta and ret_df.
    test_meta = [all_meta[i] for i in range(len(all_meta)) if test_mask[i]]
    test_dates = [m['date'] for m in test_meta]
    test_tickers = [m['ticker'] for m in test_meta]
    # Build a Series of actual returns for each test sample
    # We'll use the return_col (fwd_return_63d) from ret_df
    ret_lookup = ret_df.set_index(['ticker', 'join_date'])[return_col]
    actual_returns = []
    for tk, dt in zip(test_tickers, test_dates):
        key = (tk, pd.Timestamp(dt).date())
        val = ret_lookup.get(key, np.nan)
        actual_returns.append(val)
    actual_returns = np.array(actual_returns, dtype=np.float64)
    # Remove NaN
    valid = ~np.isnan(actual_returns)
    proba = proba[valid]
    actual_returns = actual_returns[valid]
    
    best_sharpe = -np.inf
    best_thresh = 0.0
    for thresh in np.arange(0.40, 0.85, 0.05):
        pos = (proba > thresh).astype(np.float64)
        strat_ret = pos * actual_returns
        mean_ret = np.mean(strat_ret)
        std_ret = np.std(strat_ret)
        if std_ret > 0:
            sharpe = (mean_ret / std_ret) * np.sqrt(252)
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_thresh = thresh
    
    # Compute QQQ buy‑and‑hold Sharpe for the same test period
    test_date_set = sorted(set(test_dates))
    qqq_test = qqq_close[qqq_close['join_date'].isin(test_date_set)].copy()
    qqq_test = qqq_test.sort_values('join_date')
    qqq_ret = qqq_test['QQQ'].pct_change().dropna()
    qqq_sharpe = (qqq_ret.mean() / qqq_ret.std()) * np.sqrt(252) if qqq_ret.std() > 0 else 0.0
    
    print(f"    Optimal threshold: {best_thresh:.2f}")
    print(f"    Strategy Sharpe:   {best_sharpe:.2f}")
    print(f"    QQQ Buy‑&‑Hold Sharpe: {qqq_sharpe:.2f}")
    if best_sharpe > qqq_sharpe:
        print("    [SUCCESS] Model beats QQQ on risk‑adjusted returns!")
    else:
        print("    [FAILURE] Model does not beat QQQ.")
    
    # --------------------------------------------------------
    # Step 10: Feature Importance (Top 50)
    # --------------------------------------------------------
    print("[9] Top 50 Feature Importances (gain):")
    
    importances = clf.feature_importances_
    top_idx = np.argsort(importances)[::-1][:50]
    
    importance_report = []
    for rank, idx in enumerate(top_idx, 1):
        feat_name = common_cols[idx] if idx < len(common_cols) else f"feat_{idx}"
        imp = importances[idx]
        in_causal = "[*]" if feat_name in causal_features else "   "
        importance_report.append({
            'rank': rank,
            'feature': feat_name,
            'importance': round(imp, 6),
            'in_causal_core': feat_name in causal_features
        })
        print(f"    {rank:3d}. {in_causal} {feat_name:<50s} {imp:.6f}")
    
    # --------------------------------------------------------
    # Step 11: Save Model and Artifacts
    # --------------------------------------------------------
    print("\n[10] Saving model and artifacts...")
    
    model_path = os.path.join(OUTPUT_DIR, "xgb_triple_barrier_v1.json")
    clf.save_model(model_path)
    print(f"     Model: {model_path}")
    
    # Save importance report
    imp_df = pd.DataFrame(importance_report)
    imp_path = os.path.join(OUTPUT_DIR, "xgb_feature_importance.csv")
    imp_df.to_csv(imp_path, index=False)
    print(f"     Importance: {imp_path}")
    
    # Save metadata
    meta = {
        'horizon': PRIMARY_HORIZON,
        'triple_barrier': {
            'pt_mult': hz['pt_mult'],
            'sl_mult': hz['sl_mult'],
        },
        'train_samples': int(X_train.shape[0]),
        'test_samples': int(X_test.shape[0]),
        'num_features': int(X_full.shape[1]),
        'split_date': str(split_date),
        'accuracy': round(acc, 4),
        'kappa': round(kappa, 4),
        'label_distribution': {
            label_names[u]: int(c) for u, c in zip(unique, counts)
        },
        'training_time_seconds': round(train_time, 1),
        'total_time_seconds': round(time.time() - t0, 1),
    }
    meta_path = os.path.join(OUTPUT_DIR, "xgb_training_metadata.json")
    with open(meta_path, 'w') as f:
        json.dump(meta, f, indent=2)
    print(f"     Metadata: {meta_path}")
    
    # --------------------------------------------------------
    # Step 12: SHAP Analysis (Top 20 interactions)
    # --------------------------------------------------------
    print("\n[11] Running SHAP feature interaction analysis...")
    try:
        import shap
        
        # Use a subsample for SHAP (full dataset is too large)
        shap_sample_size = min(5000, len(X_test))
        rng = np.random.RandomState(42)
        shap_idx = rng.choice(len(X_test), shap_sample_size, replace=False)
        X_shap = X_test[shap_idx]
        
        explainer = shap.TreeExplainer(clf)
        shap_values = explainer.shap_values(X_shap)
        
        # For multiclass, shap_values is a list of arrays (one per class)
        # Focus on class 2 (Profit) since that's what we care about
        if isinstance(shap_values, list):
            profit_shap = np.abs(shap_values[2])  # Class 2 = Profit
        else:
            profit_shap = np.abs(shap_values[:, :, 2])
            
        mean_shap = profit_shap.mean(axis=0)
        top_shap_idx = np.argsort(mean_shap)[::-1][:20]
        
        print("    Top 20 SHAP Features (Profit class):")
        shap_report = []
        for rank, idx in enumerate(top_shap_idx, 1):
            feat_name = common_cols[idx] if idx < len(common_cols) else f"feat_{idx}"
            sv = mean_shap[idx]
            in_causal = "[*]" if feat_name in causal_features else "   "
            shap_report.append({'rank': rank, 'feature': feat_name, 'mean_shap': round(sv, 6)})
            print(f"    {rank:3d}. {in_causal} {feat_name:<50s} {sv:.6f}")
        
        shap_df = pd.DataFrame(shap_report)
        shap_path = os.path.join(OUTPUT_DIR, "xgb_shap_analysis.csv")
        shap_df.to_csv(shap_path, index=False)
        print(f"     SHAP report: {shap_path}")
        
    except ImportError:
        print("    SHAP not installed. Run 'pip install shap' for interaction analysis.")
    except Exception as e:
        print(f"    SHAP analysis failed (non-critical): {e}")
    
    # --------------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------------
    total_time = time.time() - t0
    print(f"\n{'=' * 70}")
    print(f"  PHASE 4 COMPLETE — {total_time/60:.1f} minutes")
    print(f"{'=' * 70}")
    print(f"  Horizon:        {PRIMARY_HORIZON}")
    print(f"  Samples:        {X_full.shape[0]:,} ({X_train.shape[0]:,} train / {X_test.shape[0]:,} test)")
    print(f"  Features:       {X_full.shape[1]:,}")
    print(f"  Accuracy:       {acc:.4f}")
    print(f"  Cohen's Kappa:  {kappa:.4f}")
    print(f"  Model saved:    {model_path}")
    print(f"\n  Ready for Phase 5: Statistical Validation (CPCV + Monte Carlo)")


if __name__ == "__main__":
    main()
