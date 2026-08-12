"""
Phase 2: Causal Discovery — PCMCI on Continuous Entity Features
===============================================================
Feeds the continuous orbital trajectories of the 8 causal entities
(identified by the BQ Sieve) into PCMCI to discover direct causal
links to forward returns.

Strategy:
- Use PRIMARY continuous features per entity (lon_sin, lon_cos, speed)
- Add the 8 Dasha binary signals that survived the sieve
- Run PCMCI per ticker (preserving time-series structure)
- Aggregate causal links across tickers (frequency voting)
- Output: causal_core.csv — the features for Phase 3 (FNO)

This runs ONE TICKER AT A TIME to avoid OOM.
"""
import pandas as pd
import numpy as np
import glob
import os
import warnings
warnings.filterwarnings('ignore')

from tigramite import data_processing as pp
from tigramite.pcmci import PCMCI
from tigramite.independence_tests.parcorr import ParCorr

FEATURES_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\features_partitioned"
RETURNS_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_returns.parquet"
OUTPUT_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\causal_core.csv"

# Primary continuous features per entity (FNO needs these)
# We use lon_sin + lon_cos (preserves continuous manifold) + speed
ENTITIES = ["Sun", "Moon", "Mars", "Mercury", "Venus", "Jupiter", "Saturn", "Rahu", "Ketu"]
PRIMARY_FEATURES = []
for e in ENTITIES:
    PRIMARY_FEATURES.extend([f"{e}_lon_sin", f"{e}_lon_cos", f"{e}_speed"])

# Add Rahu/Ketu don't have speed in some configs
# Also add the Dasha signals that survived the sieve
DASHA_FEATURES = ["dasha_Sun", "dasha_Moon", "dasha_Mars", "dasha_Mercury", 
                   "dasha_Venus", "dasha_Jupiter", "dasha_Rahu", "dasha_Ketu",
                   "dasha_Saturn", "dasha_mahadasha_pct", "sade_sati_active"]

# Key aspect distances (inter-entity continuous measures)
ASPECT_FEATURES = [
    "asp_Sun_Moon_dist", "asp_Sun_Saturn_dist", "asp_Sun_Jupiter_dist",
    "asp_Moon_Saturn_dist", "asp_Moon_Rahu_dist", "asp_Mars_Saturn_dist",
    "asp_Jupiter_Saturn_dist", "asp_Venus_Saturn_dist", "asp_Mercury_Ketu_dist",
]

ALL_CANDIDATE_FEATURES = PRIMARY_FEATURES + DASHA_FEATURES + ASPECT_FEATURES
TARGET = "fwd_return_63d"  # Strongest signal horizon from sieve

MAX_LAG = 5  # Trading days of lag
TOP_TICKERS = 20  # Process top N tickers by data length for speed

def run_pcmci_for_ticker(ticker, ret_df):
    """Run PCMCI for a single ticker. Returns list of (feature, lag, strength, p_val)."""
    ticker_path = os.path.join(FEATURES_DIR, f"ticker={ticker}")
    year_files = glob.glob(os.path.join(ticker_path, "**", "*.parquet"), recursive=True)
    
    if not year_files:
        return []
    
    ticker_dfs = [pd.read_parquet(f) for f in year_files]
    feat = pd.concat(ticker_dfs, ignore_index=True).copy()
    feat['date_key'] = pd.to_datetime(feat['date']).dt.date.astype(str)
    
    ret_ticker = ret_df[ret_df['ticker'] == ticker]
    merged = feat.merge(ret_ticker[['date_key', TARGET]], on='date_key', how='inner')
    merged = merged.sort_values('date').reset_index(drop=True)
    
    if len(merged) < 200:
        return []
    
    # Select available features
    available = [f for f in ALL_CANDIDATE_FEATURES if f in merged.columns]
    available.append(TARGET)
    
    # Build clean matrix
    ts = merged[available].dropna()
    
    if len(ts) < 200:
        return []
    
    # Standardize continuous features
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    ts_scaled = pd.DataFrame(scaler.fit_transform(ts), columns=ts.columns)
    
    # Run PCMCI
    dataframe = pp.DataFrame(ts_scaled.values, 
                             datatime={0: np.arange(len(ts_scaled))},
                             var_names=list(ts_scaled.columns))
    
    cond_ind_test = ParCorr(significance='analytic')
    pcmci = PCMCI(dataframe=dataframe, cond_ind_test=cond_ind_test, verbosity=0)
    
    results = pcmci.run_pcmci(tau_max=MAX_LAG, pc_alpha=0.05)
    
    # Extract links TO the target variable
    target_idx = list(ts_scaled.columns).index(TARGET)
    p_matrix = results['p_matrix']
    val_matrix = results['val_matrix']
    
    causal_links = []
    for var_idx, var_name in enumerate(ts_scaled.columns):
        if var_name == TARGET:
            continue
        for lag in range(1, MAX_LAG + 1):
            p_val = p_matrix[var_idx, target_idx, lag]
            if p_val < 0.05:  # Significant at 5%
                strength = val_matrix[var_idx, target_idx, lag]
                causal_links.append({
                    'feature': var_name,
                    'lag': lag,
                    'strength': round(float(strength), 6),
                    'p_value': round(float(p_val), 6),
                    'ticker': ticker
                })
    
    return causal_links

def run_causal_pipeline():
    print("=" * 60)
    print("PHASE 2: PCMCI CAUSAL DISCOVERY")
    print("=" * 60)
    
    # Load returns
    ret_df = pd.read_parquet(RETURNS_PATH)
    ret_df['date_key'] = pd.to_datetime(ret_df['date']).dt.date.astype(str)
    
    # Get tickers sorted by data availability (longest first)
    ticker_dirs = [d for d in os.listdir(FEATURES_DIR) if d.startswith("ticker=")]
    tickers = [d.split("=")[1] for d in ticker_dirs]
    
    # Use top N tickers by file count (proxy for data length)
    ticker_sizes = []
    for t in tickers:
        tp = os.path.join(FEATURES_DIR, f"ticker={t}")
        nfiles = len(glob.glob(os.path.join(tp, "**", "*.parquet"), recursive=True))
        ticker_sizes.append((t, nfiles))
    ticker_sizes.sort(key=lambda x: x[1], reverse=True)
    selected = [t for t, _ in ticker_sizes[:TOP_TICKERS]]
    
    print(f"Running PCMCI on {len(selected)} tickers (top by data length)")
    print(f"Features: {len(ALL_CANDIDATE_FEATURES)} candidates + 1 target")
    print(f"Target: {TARGET}, Max lag: {MAX_LAG}")
    
    # Run PCMCI per ticker
    all_links = []
    for i, ticker in enumerate(selected):
        print(f"  [{i+1}/{len(selected)}] {ticker}...", end=" ", flush=True)
        try:
            links = run_pcmci_for_ticker(ticker, ret_df)
            all_links.extend(links)
            print(f"{len(links)} causal links found")
        except Exception as e:
            print(f"ERROR: {e}")
    
    if not all_links:
        print("\nNo causal links found! The pipeline may need recalibration.")
        return
    
    # Aggregate: frequency voting across tickers
    links_df = pd.DataFrame(all_links)
    
    # Count how many tickers each feature appears in
    freq = links_df.groupby('feature').agg(
        ticker_count=('ticker', 'nunique'),
        mean_strength=('strength', 'mean'),
        mean_pval=('p_value', 'mean'),
        best_lag=('lag', lambda x: x.mode().iloc[0] if len(x) > 0 else 0)
    ).reset_index()
    
    # Require at least 3 tickers for robustness
    MIN_TICKER_VOTES = 3
    causal_core = freq[freq['ticker_count'] >= MIN_TICKER_VOTES].sort_values(
        'ticker_count', ascending=False
    )
    
    causal_core.to_csv(OUTPUT_PATH, index=False)
    
    print(f"\n{'='*60}")
    print(f"CAUSAL DISCOVERY COMPLETE")
    print(f"{'='*60}")
    print(f"Total causal links found: {len(links_df)}")
    print(f"Unique features with links: {links_df['feature'].nunique()}")
    print(f"Features passing frequency vote (>={MIN_TICKER_VOTES} tickers): {len(causal_core)}")
    print(f"\nCausal Core ({len(causal_core)} features):")
    print(causal_core.to_string(index=False))
    print(f"\nOutput: {OUTPUT_PATH}")

if __name__ == "__main__":
    run_causal_pipeline()
