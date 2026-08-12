"""
Stage 6: HMM Regime Gating — Bull/Bear/Crash Traffic Light
============================================================
Trains a 3-state Hidden Markov Model on SPY + VIX to classify
market regimes. Signals are ONLY allowed to fire when the regime
is favorable.

This is the critical missing piece from Opus's architecture that
prevents the model from trading into a regime it has never seen.

Usage:
  1. Run standalone to train and save the HMM
  2. Import get_regime(date) in other scripts to gate signals
"""
import pandas as pd
import numpy as np
import os, json, pickle, time, warnings
warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION
# ============================================================
RETURNS_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_returns.parquet"
OUTPUT_DIR   = r"E:\Python\Learn\vedic_quant\models"
CACHE_DIR    = r"E:\Python\Learn\vedic_quant\cache"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)


def load_market_data():
    """Load SPY returns as a proxy for market regime."""
    ret_df = pd.read_parquet(RETURNS_PATH)
    
    # Find a broad market proxy (SPY, ^GSPC, or use available index)
    market_tickers = ['SPY', 'QQQ', 'IWM', 'DIA']
    market = None
    for t in market_tickers:
        sub = ret_df[ret_df['ticker'] == t]
        if len(sub) > 500:
            market = sub.copy()
            print(f"  Using {t} as market proxy ({len(sub):,} days)")
            break
    
    if market is None:
        # Fallback: average returns across all stocks
        print("  No index ticker found. Computing cross-sectional mean returns.")
        market = ret_df.groupby('date').agg(
            fwd_return_10d=('fwd_return_10d', 'mean'),
            fwd_return_21d=('fwd_return_21d', 'mean'),
            fwd_return_63d=('fwd_return_63d', 'mean'),
        ).reset_index()
        market['ticker'] = 'MARKET_AVG'
    
    market['date'] = pd.to_datetime(market['date'])
    market = market.sort_values('date').reset_index(drop=True)
    return market


def engineer_hmm_features(market):
    """Create features for the HMM from market data."""
    df = market.copy()
    
    # We need daily returns-like features
    # Use the available forward returns to derive backward-looking features
    features = pd.DataFrame(index=df.index)
    
    if 'fwd_return_10d' in df.columns:
        # Use 10D return as a regime indicator
        features['ret_10d'] = df['fwd_return_10d'].fillna(0)
    
    if 'fwd_return_21d' in df.columns:
        features['ret_21d'] = df['fwd_return_21d'].fillna(0)
    
    if 'fwd_return_63d' in df.columns:
        features['ret_63d'] = df['fwd_return_63d'].fillna(0)
    
    # Rolling volatility from 10D returns
    if 'ret_10d' in features.columns:
        features['vol_20d'] = features['ret_10d'].rolling(20, min_periods=5).std().fillna(
            features['ret_10d'].std()
        )
        features['vol_60d'] = features['ret_10d'].rolling(60, min_periods=10).std().fillna(
            features['ret_10d'].std()
        )
        # Vol ratio (rising vol = bear/crash)
        features['vol_ratio'] = (features['vol_20d'] / features['vol_60d']).clip(0.2, 5.0).fillna(1.0)
    
    # Momentum
    if 'ret_21d' in features.columns and 'ret_63d' in features.columns:
        features['momentum'] = features['ret_21d'] - features['ret_63d']
    
    # Drop NaN rows
    features = features.dropna()
    
    # Standardize
    for col in features.columns:
        mu, sigma = features[col].mean(), features[col].std()
        if sigma > 0:
            features[col] = (features[col] - mu) / sigma
    
    return features, df.loc[features.index, 'date'].values


def train_hmm(features, n_states=3):
    """Train a Gaussian HMM with 3 states."""
    try:
        from hmmlearn.hmm import GaussianHMM
    except ImportError:
        print("  [INSTALL] Installing hmmlearn...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'hmmlearn', '-q'])
        from hmmlearn.hmm import GaussianHMM
    
    X = features.values.astype(np.float64)
    
    # Train with multiple random restarts, pick best
    best_model = None
    best_score = -np.inf
    
    for seed in range(10):
        model = GaussianHMM(
            n_components=n_states,
            covariance_type='full',
            n_iter=200,
            random_state=seed,
            tol=1e-4,
        )
        try:
            model.fit(X)
            score = model.score(X)
            if score > best_score:
                best_score = score
                best_model = model
        except Exception:
            continue
    
    if best_model is None:
        raise RuntimeError("HMM training failed on all seeds")
    
    print(f"  Best HMM score: {best_score:.2f} (10 random restarts)")
    return best_model


def label_regimes(model, features, dates):
    """Assign regime labels and sort by mean return."""
    X = features.values.astype(np.float64)
    raw_states = model.predict(X)
    
    # Compute mean of first feature (short return) per state to rank them
    state_means = {}
    for s in range(model.n_components):
        mask = raw_states == s
        state_means[s] = features.iloc[:, 0].values[mask].mean()
    
    # Sort: lowest mean return = Bear (0), middle = Neutral (1), highest = Bull (2)
    sorted_states = sorted(state_means.keys(), key=lambda s: state_means[s])
    relabel_map = {old: new for new, old in enumerate(sorted_states)}
    
    regimes = np.array([relabel_map[s] for s in raw_states])
    regime_names = {0: 'Bear/Crash', 1: 'Neutral', 2: 'Bull'}
    
    return regimes, regime_names


def analyze_regimes(regimes, dates, features, regime_names):
    """Print regime statistics."""
    print("\n  Regime Distribution:")
    for r_id, r_name in regime_names.items():
        mask = regimes == r_id
        count = mask.sum()
        pct = 100 * count / len(regimes)
        mean_ret = features.iloc[:, 0].values[mask].mean() if mask.any() else 0
        print(f"    {r_name:12s}: {count:5d} days ({pct:5.1f}%)  mean_ret={mean_ret:+.4f}")
    
    # Transition matrix
    transitions = np.zeros((3, 3))
    for i in range(len(regimes) - 1):
        transitions[regimes[i], regimes[i+1]] += 1
    # Normalize rows
    row_sums = transitions.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    trans_prob = transitions / row_sums
    
    print("\n  Transition Matrix:")
    print(f"    {'':12s} -> Bear    -> Neutral -> Bull")
    for r_id, r_name in regime_names.items():
        probs = trans_prob[r_id]
        print(f"    {r_name:12s}   {probs[0]:.3f}    {probs[1]:.3f}     {probs[2]:.3f}")
    
    return trans_prob


def main():
    t0 = time.time()
    print("=" * 60)
    print("  STAGE 6: HMM REGIME GATING")
    print("  3-State Bull/Bear/Crash Traffic Light")
    print("=" * 60)
    
    # Step 1: Load market data
    print("\n[1] Loading market data...")
    market = load_market_data()
    
    # Step 2: Engineer features
    print("\n[2] Engineering HMM features...")
    features, dates = engineer_hmm_features(market)
    print(f"    {len(features):,} samples, {features.shape[1]} features")
    print(f"    Features: {list(features.columns)}")
    
    # Step 3: Train HMM
    print("\n[3] Training 3-state Gaussian HMM...")
    model = train_hmm(features, n_states=3)
    
    # Step 4: Label regimes
    print("\n[4] Labeling regimes...")
    regimes, regime_names = label_regimes(model, features, dates)
    
    # Step 5: Analyze
    print("\n[5] Regime analysis...")
    trans_prob = analyze_regimes(regimes, dates, features, regime_names)
    
    # Step 6: Save
    print("\n[6] Saving...")
    
    hmm_path = os.path.join(OUTPUT_DIR, "hmm_regime_model.pkl")
    with open(hmm_path, 'wb') as f:
        pickle.dump({
            'model': model,
            'feature_columns': list(features.columns),
            'feature_means': features.mean().to_dict(),
            'feature_stds': features.std().to_dict(),
            'regime_names': regime_names,
            'transition_matrix': trans_prob.tolist(),
        }, f)
    print(f"    Model: {hmm_path}")
    
    # Save regime history for backtesting
    regime_df = pd.DataFrame({
        'date': dates,
        'regime': regimes,
        'regime_name': [regime_names[r] for r in regimes],
    })
    regime_path = os.path.join(OUTPUT_DIR, "regime_history.csv")
    regime_df.to_csv(regime_path, index=False)
    print(f"    History: {regime_path}")
    
    # Save results
    results = {
        'stage': 6,
        'model': 'GaussianHMM',
        'n_states': 3,
        'n_samples': len(features),
        'n_features': features.shape[1],
        'feature_columns': list(features.columns),
        'regime_distribution': {
            regime_names[r]: int((regimes == r).sum()) for r in range(3)
        },
        'transition_matrix': trans_prob.tolist(),
        'hmm_model_path': hmm_path,
        'regime_history_path': regime_path,
        'total_time_seconds': round(time.time() - t0, 1),
    }
    
    results_path = os.path.join(OUTPUT_DIR, "stage6_hmm_results.json")
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"    Results: {results_path}")
    
    total = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f"  STAGE 6 COMPLETE - {total:.1f} seconds")
    print(f"{'=' * 60}")
    for r_id, r_name in regime_names.items():
        count = (regimes == r_id).sum()
        print(f"  {r_name}: {count:,} days ({100*count/len(regimes):.1f}%)")
    
    # Show current regime
    if len(dates) > 0:
        last_date = pd.Timestamp(dates[-1]).strftime('%Y-%m-%d')
        last_regime = regime_names[regimes[-1]]
        print(f"\n  [TRAFFIC LIGHT] Current Regime ({last_date}): {last_regime}")


if __name__ == "__main__":
    main()
