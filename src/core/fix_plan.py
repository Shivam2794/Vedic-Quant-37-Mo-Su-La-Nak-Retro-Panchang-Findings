import os
import re

file_path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\35732b90-976f-4cc4-b3fe-7fc24c167fe0\next_phase_plan.md"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix 1: DataEng_2 - tzinfo=timezone.utc
content = content.replace(
    'from datetime import datetime',
    'from datetime import datetime, timezone'
)
content = content.replace(
    'datetime(1990, 1, 22, 5, 0, 0)', 'datetime(1990, 1, 22, 5, 0, 0, tzinfo=timezone.utc)'
).replace(
    'datetime(1993, 1, 29, 14, 30, 0)', 'datetime(1993, 1, 29, 14, 30, 0, tzinfo=timezone.utc)'
).replace(
    'datetime(1999, 3, 4, 5, 0, 0)', 'datetime(1999, 3, 4, 5, 0, 0, tzinfo=timezone.utc)'
).replace(
    'datetime(1999, 3, 10, 14, 30, 0)', 'datetime(1999, 3, 10, 14, 30, 0, tzinfo=timezone.utc)'
).replace(
    'datetime(1776, 7, 4, 22, 10, 36)', 'datetime(1776, 7, 4, 22, 10, 36, tzinfo=timezone.utc)'
)

# Fix 2: DataEng_4 - market_open_utc
old_market_open = """def market_open_utc(trading_date: date, tz: str = "America/New_York") -> datetime:
    eastern = pytz.timezone(tz)
    local_open = eastern.localize(
        datetime(trading_date.year, trading_date.month, trading_date.day, 9, 30, 0),
        is_dst=None 
    )
    return local_open.astimezone(timezone.utc)"""

new_market_open = """import pandas_market_calendars as mcal
def market_open_utc(trading_date: date, exchange: str = "NYSE") -> datetime:
    nyse = mcal.get_calendar(exchange)
    schedule = nyse.schedule(start_date=trading_date, end_date=trading_date)
    if schedule.empty:
        raise ValueError(f"Market closed on {trading_date}")
    return schedule.iloc[0]['market_open'].to_pydatetime()"""
content = content.replace(old_market_open, new_market_open)

# Fix 3: DataEng_3 & ML_4 - generate_feature_tensor
old_gen = """    # Implements multiprocessing with chunked row-groups.
    # Uses Planet-specific sigmas: PLANET_SIGMA dict.
    pass"""
new_gen = """    # Implements multiprocessing with deterministic partition writing (checkpoint_dir/date=YYYY-MM/part.parquet)
    # Uses 'overwrite' mode for strict idempotency.
    # Target Labels MUST be Open-to-Close (Intraday) returns or T+1 Open-to-Open.
    pass"""
content = content.replace(old_gen, new_gen)

# Fix 4: Vedic_1 - FLG_SIDEREAL ONLY
content = content.replace('FLG_SIDEREAL ONLY', 'FLG_SIDEREAL + SIDM_LAHIRI')
content = content.replace(
    'enforce `swe.FLG_SIDEREAL` and use',
    'enforce `swe.FLG_SIDEREAL` + `swe.set_sid_mode(swe.SIDM_LAHIRI)` and use'
)

# Fix 5: Vedic_2 - Go/No-Go Gate
content = content.replace(
    'Moon on 2004-01-02 must be in Rohini, NOT Mrigashira',
    'Jan 4, 2004 02:00 UTC: Tropical Moon in Mrigashira, Lahiri in Rohini'
)

# Fix 6: ML_1, DataEng_1, Vedic_3, Vedic_4 - Phase 2 Rewrite
old_phase2 = """## Phase 2: Signal Extraction & Pre-Filtering

### 2.1 Hybrid Causal Pre-Filter
Due to sample-size constraints and the quasi-periodic nature of planetary cycles, all 2,463+ features must pass a rigorous, cycle-aware causal pre-filter before touching the neural network.

**File: `ml_pipeline/causal_pre_filter.py`**
```python
def hybrid_granger_spearman_filter(
    feature_df: pd.DataFrame, 
    target_returns: pd.Series, 
    planet_speeds: dict
) -> list[str]:
    \"\"\"
    Fast planets (Moon, Mercury, Venus, Mars):
      - Method: Rolling Granger causality on differenced features
      - Window: Planet-specific (Moon: 90d, Inner: 252d, Mars: 780d)
      - Passing: F-test p < 0.10 in >= 3 of 5 recent windows
      
    Slow planets (Jupiter, Saturn, Uranus, Neptune, Pluto, Nodes):
      - Method: Full-sample Spearman correlation
      - Window: Full dataset
      - Passing: |ρ| > 0.08 and consistent sign across splits
    \"\"\"
    pass

def elastic_net_purge(surviving_features: list[str], target_labels: pd.Series) -> list[str]:
    \"\"\"
    Applies PurgedKFold(n_splits=5, embargo=21, purge=10) with ElasticNet(alpha=0.7).
    Must survive in >= 3 of 5 CV folds. Expected output: 50-80 features.
    \"\"\"
    pass
```

### 🛑 PHASE 2 GO/NO-GO GATE
- **Criteria**: The pre-filter must reduce the feature space from ~3,000 to a defensible 50-80 feature bottleneck.
- **Specific Check**: The Feature-to-Sample ratio must be ≥ 20 (e.g., 80 features for 5,040 samples = 63 ratio ✅)."""

new_phase2 = """## Phase 2: Signal Extraction & Pre-Filtering

### 2.1 Hybrid Causal Pre-Filter (Nested CV)
To prevent fatal data leakage, the causal pre-filter is implemented as an `sklearn.base.BaseEstimator` and executes **strictly inside** the training loop of each Phase 4 Walk-Forward fold. All filtering uses only $t \le T_{train}$.

**File: `ml_pipeline/causal_pre_filter.py`**
```python
from sklearn.base import BaseEstimator, TransformerMixin

class CausalPreFilter(BaseEstimator, TransformerMixin):
    \"\"\"
    Strictly applied within Walk-Forward CV folds to prevent lookahead bias.
    - Continuous features (Harmonics): Rolling Granger causality or Spearman.
    - Categorical features (Nakshatras, Rasis): Mutual Information (MI) or Kruskal-Wallis.
    - Trans-Saturnians (Uranus, Neptune, Pluto) are EXCLUDED from Vedic dignities.
    \"\"\"
    def fit(self, X_train: pd.DataFrame, y_train: pd.Series):
        # 1. Filter Continuous Features (Granger/Spearman up to T_train)
        # 2. Filter Categorical Features (MI/Kruskal-Wallis up to T_train)
        # 3. Applies ElasticNet purge
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        # Return only the surviving 50-80 features
        pass
```

### 🛑 PHASE 2 GO/NO-GO GATE
- **Criteria**: The pre-filter reduces the feature space from ~3,000 to a defensible 50-80 feature bottleneck *within each CV fold*.
- **Specific Check**: The Feature-to-Sample ratio must be ≥ 20 (e.g., 80 features for 5,040 samples = 63 ratio ✅) without leaking future data."""
content = content.replace(old_phase2, new_phase2)

# Fix 7: ML_2 - Continuous Branch Preprocessing
content = content.replace('arcsin_sqrt preproc', 'StandardScaler preproc')

# Fix 8: Vedic_5 - Neural Net Indexing Crash
content = content.replace(
    'nn.ModuleList([nn.Embedding(27, 8) for _ in categorical_dims])',
    'nn.ModuleList([nn.Embedding(dim_size + 1, 8) for dim_size in categorical_dims])'
)

# Fix 9: ML_3 & Vedic_6 - H0.1 and H0.2
old_h01 = """def h0_1_permutation_test(pipeline, real_data: pd.DataFrame, iterations: int = 1000):
    \"\"\"
    Independently permutes feature columns to destroy cross-sectional correlations 
    while preserving auto-correlation. Requires p < 0.05 against real Sharpe.
    \"\"\"
    pass"""

new_h01 = """def h0_1_permutation_test(pipeline, real_data: pd.DataFrame, iterations: int = 1000):
    \"\"\"
    Uses Circular/Phase-Shift Permutation or Stationary Block Bootstrapping to destroy 
    signal while preserving auto-correlation. Requires p < 0.05 against real Sharpe.
    \"\"\"
    pass"""
content = content.replace(old_h01, new_h01)

old_h02 = """def h0_2_phase_shift_test(pipeline, natal_date: datetime, planet_class: str):
    \"\"\"
    Retrains on shifted natal dates.
    Moon: ±{1, 3, 7, 14} days
    Sun/Inner: ±{7, 14, 30, 60} days
    Saturn: ±{180, 365, 730, 1095} days
    Real natal date must be in top quartile of Sharpe across all offsets.
    \"\"\"
    pass"""

new_h02 = """def h0_2_phase_shift_test(pipeline, natal_date: datetime, planet_class: str):
    \"\"\"
    Retrains on shifted natal dates.
    Moon: ±{3, 7, 11, 19} days (avoids ±14 anti-phase symmetry)
    Sun/Inner: ±{7, 14, 30, 60} days
    Saturn: ±{180, 365, 730, 1095} days
    Real natal date must be in top quartile of Sharpe across all offsets.
    \"\"\"
    pass"""
content = content.replace(old_h02, new_h02)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updates completed successfully.")
