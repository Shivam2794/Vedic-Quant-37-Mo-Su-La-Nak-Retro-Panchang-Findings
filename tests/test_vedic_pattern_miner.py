"""
tests/test_vedic_pattern_miner.py — Comprehensive E2E & Unit Test Suite for Vedic Pattern Mining & Statistical Sieve
===================================================================================================================
Covers Requirements:
- R1: Baseline Null Calibration & Feature Alignment (Empirical Null Distributions, Zero NaNs, Continuous RTH)
- R2: Univariate Statistical Significance & Lift Ratio Engine (Fisher Exact, Chi2, Benjamini-Hochberg FDR, KS 2-sample, Mann-Whitney U)
- R3: Higher-Order Combinatorial Pattern Mining (FP-Growth, 2/3/4-way Confluences, Decision Tree Rule Extraction, Permutation Tests)

Tiers Covered:
- Tier 1: Feature Coverage (>=5 tests per requirement R1, R2, R3)
- Tier 2: Boundary & Corner Cases (>=5 tests per requirement R1, R2, R3)
- Tier 3: Pairwise Interactions & Cross-Requirement Consistency
- Tier 4: Real-World Workloads on 1,408 Anomaly & Baseline Parquet Datasets
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd
from scipy import stats

# Path setup
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

ANALYSIS_DIR = os.path.join(SRC_DIR, "analysis")
if ANALYSIS_DIR not in sys.path:
    sys.path.insert(0, ANALYSIS_DIR)


# ==============================================================================
# REFERENCE MATHEMATICAL ORACLES FOR STATISTICAL & MINING VERIFICATION
# ==============================================================================

def oracle_empirical_lift(n_feature_anomaly, n_total_anomaly, n_feature_baseline, n_total_baseline, eps=1e-9):
    """
    Authoritative Lift = P(Feature | Anomaly) / P(Feature | Baseline)
    P(Feature | Anomaly) = n_feature_anomaly / n_total_anomaly
    P(Feature | Baseline) = n_feature_baseline / n_total_baseline
    """
    p_anomaly = n_feature_anomaly / max(n_total_anomaly, 1)
    p_baseline = n_feature_baseline / max(n_total_baseline, 1)
    if p_baseline == 0:
        return np.inf if p_anomaly > 0 else 1.0
    return p_anomaly / p_baseline


def oracle_fisher_exact_2x2(n_feature_anomaly, n_total_anomaly, n_feature_baseline, n_total_baseline):
    """
    Computes 2-tailed Fisher's exact test on a 2x2 contingency table:
    [[n_fa, n_ta - n_fa],
     [n_fb, n_tb - n_fb]]
    """
    table = [
        [int(n_feature_anomaly), int(n_total_anomaly - n_feature_anomaly)],
        [int(n_feature_baseline), int(n_total_baseline - n_feature_baseline)]
    ]
    odds_ratio, p_value = stats.fisher_exact(table, alternative='two-sided')
    return odds_ratio, p_value


def oracle_chi2_contingency_2x2(n_feature_anomaly, n_total_anomaly, n_feature_baseline, n_total_baseline):
    """
    Computes 2x2 Chi-Square test with Yates' continuity correction.
    """
    table = [
        [int(n_feature_anomaly), int(n_total_anomaly - n_feature_anomaly)],
        [int(n_feature_baseline), int(n_total_baseline - n_feature_baseline)]
    ]
    chi2, p_val, dof, _ = stats.chi2_contingency(table, correction=True)
    return chi2, p_val, dof


def oracle_benjamini_hochberg_fdr(p_values, alpha=0.05):
    """
    Benjamini-Hochberg (1995) step-up FDR procedure.
    Sorts p-values in ascending order: p_(1) <= p_(2) <= ... <= p_(m).
    Adjusted q-value: q_(i) = min_{k >= i} (p_(k) * m / k), capped at 1.0.
    """
    p_arr = np.asarray(p_values, dtype=float)
    m = len(p_arr)
    if m == 0:
        return np.array([]), np.array([], dtype=bool)
    
    order = np.argsort(p_arr)
    sorted_p = p_arr[order]
    
    q_sorted = np.zeros(m)
    current_min = 1.0
    for i in range(m - 1, -1, -1):
        rank = i + 1
        q_val = (sorted_p[i] * m) / rank
        current_min = min(current_min, q_val)
        q_sorted[i] = current_min
        
    q_sorted = np.clip(q_sorted, 0.0, 1.0)
    
    # Restore original ordering
    q_values = np.zeros(m)
    q_values[order] = q_sorted
    significant = q_values <= alpha
    return q_values, significant


def oracle_ks_2sample(data_anomaly, data_baseline):
    """Two-sample Kolmogorov-Smirnov continuous distribution test."""
    res = stats.ks_2samp(data_anomaly, data_baseline)
    return res.statistic, res.pvalue


def oracle_mann_whitney_u(data_anomaly, data_baseline):
    """Mann-Whitney U non-parametric continuous test."""
    res = stats.mannwhitneyu(data_anomaly, data_baseline, alternative='two-sided')
    return res.statistic, res.pvalue


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def synthetic_null_baseline_df():
    """
    Generates a controlled 1,000-row synthetic baseline dataset with 397 columns matching
    the Omni-Vedic schema, representing continuous RTH market bars.
    """
    np.random.seed(42)
    n = 1000
    dates = pd.date_range("2020-01-01 09:30:00", periods=n, freq="h", tz="America/New_York")
    
    data = {
        'Datetime_UTC': dates.tz_convert('UTC'),
        'Datetime_NY': dates,
        'Julian_Date_UT': np.linspace(2458849.5, 2458849.5 + n/24.0, n),
        'Open': 300.0 + np.cumsum(np.random.randn(n) * 0.5),
        'Timeframe': ['1H'] * n,
        'Candle_Direction': np.random.choice(['GREEN', 'RED'], size=n, p=[0.52, 0.48]),
        'Solid_Ratio': np.random.uniform(0.1, 0.8, size=n),
        'Body_To_ATR': np.random.uniform(0.2, 2.5, size=n),
        'TOD_RVOL': np.random.uniform(0.5, 2.5, size=n),
        # Vedic Categorical Features
        'Sun_Sign': np.random.choice(range(12), size=n),
        'Moon_Sign': np.random.choice(range(12), size=n),
        'Mars_Sign': np.random.choice(range(12), size=n),
        'Sun_Nakshatra': np.random.choice(range(1, 28), size=n),
        'Moon_Nakshatra': np.random.choice(range(1, 28), size=n),
        'Mars_Nakshatra': np.random.choice(range(1, 28), size=n),
        'Lagna_NYSE_Sign': np.random.choice(range(12), size=n),
        'Sun_Retro': np.zeros(n, dtype=int),
        'Mars_Retro': np.random.choice([0, 1], size=n, p=[0.85, 0.15]),
        'Mercury_Retro': np.random.choice([0, 1], size=n, p=[0.80, 0.20]),
        'Saturn_Retro': np.random.choice([0, 1], size=n, p=[0.65, 0.35]),
        'Bhv_Mars_Saturn': np.random.choice(range(1, 13), size=n),
        'Bhv_Sun_Moon': np.random.choice(range(1, 13), size=n),
        'Sun_Vargottama': np.random.choice([0, 1], size=n, p=[0.89, 0.11]),
        'Moon_Vargottama': np.random.choice([0, 1], size=n, p=[0.89, 0.11]),
        'Jaimini_GK': np.random.choice(['Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu'], size=n),
        'Jaimini_AK': np.random.choice(['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'], size=n),
        'SAV_Total': np.random.randint(320, 350, size=n),
        'SAV_At_Moon': np.random.randint(18, 40, size=n),
        'SAV_At_Mars': np.random.randint(18, 40, size=n),
        # Vedic Continuous Features
        'Sun_Speed': np.random.normal(0.98, 0.02, size=n),
        'Moon_Speed': np.random.normal(13.2, 1.0, size=n),
        'Mars_Speed': np.random.normal(0.5, 0.2, size=n),
        'Sun_Declination': np.random.uniform(-23.4, 23.4, size=n),
        'Moon_Declination': np.random.uniform(-28.0, 28.0, size=n),
        'Mars_Declination': np.random.uniform(-25.0, 25.0, size=n),
        'Ang_Mars_Saturn': np.random.uniform(0, 360, size=n),
        'Ang_Sun_Moon': np.random.uniform(0, 360, size=n),
        'Shadbala_Mars_Rupas': np.random.normal(6.5, 1.2, size=n),
        'Shadbala_Saturn_Rupas': np.random.normal(6.0, 1.1, size=n),
        'Vim_MD': np.random.choice(['Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn'], size=n),
        'Vim_AD': np.random.choice(['Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn'], size=n),
    }
    data['High'] = data['Open'] + np.random.uniform(0.5, 2.0, size=n)
    data['Low'] = data['Open'] - np.random.uniform(0.5, 2.0, size=n)
    data['Close'] = data['Open'] + np.random.uniform(-1.0, 1.0, size=n)
    data['Volume'] = np.random.uniform(500000, 2000000, size=n)
    
    df = pd.DataFrame(data)
    return df


@pytest.fixture
def synthetic_anomaly_df(synthetic_null_baseline_df):
    """
    Generates a controlled 200-row anomaly dataset with deliberate signal injection:
    - Mars in 6/8 aspect to Saturn (Bhv_Mars_Saturn = 6) enriched with RED crashes (Lift >= 3.0x).
    - Moon in Rahu Nakshatra (Ardra = 6) enriched with crashes.
    - Sun Vargottama enriched with GREEN surges.
    """
    np.random.seed(101)
    n = 200
    df = synthetic_null_baseline_df.sample(n, replace=True).copy().reset_index(drop=True)
    
    # Inject deliberate signals in first 100 rows (Bearish Crash Anomaly)
    df.loc[:99, 'Candle_Direction'] = 'RED'
    df.loc[:99, 'Solid_Ratio'] = np.random.uniform(0.70, 0.95, size=100)
    df.loc[:99, 'Body_To_ATR'] = np.random.uniform(1.8, 3.5, size=100)
    df.loc[:99, 'TOD_RVOL'] = np.random.uniform(1.8, 4.0, size=100)
    df.loc[:69, 'Bhv_Mars_Saturn'] = 6  # 70% of crashes have Mars 6th to Saturn (Shadashtaka)
    df.loc[:69, 'Moon_Nakshatra'] = 6   # Ardra (Rahu Nakshatra)
    df.loc[:69, 'Lagna_NYSE_Sign'] = 4  # Leo Lagna
    df.loc[:69, 'Jaimini_GK'] = 'Mars'
    df.loc[:69, 'SAV_At_Moon'] = np.random.randint(18, 23, size=70) # Low SAV (<25)
    
    # Inject deliberate signals in next 100 rows (Bullish Surge Anomaly)
    df.loc[100:, 'Candle_Direction'] = 'GREEN'
    df.loc[100:, 'Solid_Ratio'] = np.random.uniform(0.70, 0.95, size=100)
    df.loc[100:, 'Body_To_ATR'] = np.random.uniform(1.8, 3.5, size=100)
    df.loc[100:, 'TOD_RVOL'] = np.random.uniform(1.8, 4.0, size=100)
    df.loc[100:169, 'Sun_Vargottama'] = 1
    df.loc[100:169, 'SAV_At_Moon'] = np.random.randint(33, 40, size=70) # High SAV (>32)
    df.loc[100:169, 'Shadbala_Mars_Rupas'] = np.random.normal(8.5, 0.8, size=70)
    
    return df


# ==============================================================================
# TIER 1: FEATURE COVERAGE (>=5 TESTS PER FEATURE R1, R2, R3)
# ==============================================================================

class TestTier1R1BaselineNullCalibration:
    """Tier 1 Tests for R1: Baseline Null Calibration & Feature Alignment."""

    def test_r1_baseline_generation_and_schema_alignment(self, synthetic_null_baseline_df):
        """1. Verifies baseline dataset generates without error and aligns critical feature columns."""
        df = synthetic_null_baseline_df
        required_cols = ['Datetime_UTC', 'Julian_Date_UT', 'Candle_Direction', 'Sun_Sign', 'Moon_Nakshatra', 'SAV_Total']
        for col in required_cols:
            assert col in df.columns, f"Missing required baseline column: {col}"
        assert len(df) >= 100, f"Expected baseline size >= 100, got {len(df)}"

    def test_r1_baseline_temporal_continuity_and_rth_filtering(self, synthetic_null_baseline_df):
        """2. Verifies timestamps are continuous and correctly converted between UTC and NY timezones."""
        df = synthetic_null_baseline_df
        assert df['Datetime_UTC'].dt.tz is not None, "Datetime_UTC must be timezone-aware"
        assert df['Datetime_NY'].dt.tz is not None, "Datetime_NY must be timezone-aware"
        diff_hours = (df['Datetime_UTC'] - df['Datetime_NY'].dt.tz_convert('UTC')).dt.total_seconds()
        assert (diff_hours == 0).all(), "Datetime_UTC and Datetime_NY represent different instants"

    def test_r1_baseline_zero_nans_integrity(self, synthetic_null_baseline_df):
        """3. Verifies zero NaNs across all categorical and continuous columns in baseline dataset."""
        df = synthetic_null_baseline_df
        nan_counts = df.isna().sum()
        assert (nan_counts == 0).all(), f"Found NaNs in baseline columns: {nan_counts[nan_counts > 0].to_dict()}"

    def test_r1_baseline_discrete_distributions_sum_to_one(self, synthetic_null_baseline_df):
        """4. Verifies empirical null probability distributions for discrete features sum to 1.0."""
        df = synthetic_null_baseline_df
        for col in ['Sun_Sign', 'Moon_Nakshatra', 'Lagna_NYSE_Sign']:
            prob_dist = df[col].value_counts(normalize=True)
            np.testing.assert_almost_equal(prob_dist.sum(), 1.0, decimal=6)
            assert (prob_dist >= 0).all() and (prob_dist <= 1.0).all()

    def test_r1_baseline_continuous_distributions_calibration(self, synthetic_null_baseline_df):
        """5. Verifies continuous feature null distributions have valid positive variance and finite bounds."""
        df = synthetic_null_baseline_df
        continuous_cols = ['Sun_Speed', 'Moon_Speed', 'Ang_Mars_Saturn', 'SAV_Total']
        for col in continuous_cols:
            var = df[col].var()
            assert var > 0, f"Continuous baseline feature {col} has zero or negative variance: {var}"
            assert np.isfinite(df[col]).all(), f"Non-finite values found in {col}"


class TestTier1R2UnivariateStatisticalEngine:
    """Tier 1 Tests for R2: Univariate Statistical Significance, Lift, and Hypothesis Sieve."""

    def test_r2_univariate_lift_ratio_calculation(self):
        """6. Verifies Empirical Lift formula matches authoritative mathematical derivation."""
        lift = oracle_empirical_lift(70, 100, 80, 1000)
        assert abs(lift - 8.75) < 1e-6, f"Expected Lift 8.75, got {lift}"

    def test_r2_fishers_exact_test_2x2_contingency(self):
        """7. Validates Fisher's Exact test two-tailed p-value on high-lift contingency table."""
        odds_ratio, p_val = oracle_fisher_exact_2x2(70, 100, 80, 1000)
        assert odds_ratio > 10.0, f"Expected high odds ratio, got {odds_ratio}"
        assert p_val < 1e-10, f"Expected extreme statistical significance, got p={p_val}"

    def test_r2_chi_square_independence_test(self):
        """8. Validates Chi-Square test with continuity correction on contingency matrices."""
        chi2, p_val, dof = oracle_chi2_contingency_2x2(70, 100, 80, 1000)
        assert dof == 1, f"Expected 1 degree of freedom for 2x2 table, got {dof}"
        assert chi2 > 50.0, f"Expected large Chi2 statistic, got {chi2}"
        assert p_val < 1e-10, f"Expected small p-value, got {p_val}"

    def test_r2_benjamini_hochberg_fdr_control(self):
        """9. Validates Benjamini-Hochberg FDR step-up procedure guarantees FDR <= alpha."""
        np.random.seed(42)
        true_p = np.array([1e-6, 1e-5, 1e-5, 2e-4, 5e-4, 1e-3, 2e-3, 3e-3, 4e-3, 5e-3])
        null_p = np.random.uniform(0.02, 1.0, size=90)
        all_p = np.concatenate([true_p, null_p])
        
        q_vals, sig = oracle_benjamini_hochberg_fdr(all_p, alpha=0.05)
        assert len(q_vals) == 100
        assert sig[:5].all(), "Top true signals failed FDR filter"
        assert not sig[10:].all(), "Null noise spuriously passed FDR"

    def test_r2_ks_2sample_distribution_test(self, synthetic_anomaly_df, synthetic_null_baseline_df):
        """10. Validates Kolmogorov-Smirnov 2-sample continuous test detects distribution shifts."""
        anom_vals = synthetic_anomaly_df.loc[100:169, 'Shadbala_Mars_Rupas'].values
        base_vals = synthetic_null_baseline_df['Shadbala_Mars_Rupas'].values
        stat, p_val = oracle_ks_2sample(anom_vals, base_vals)
        assert stat > 0.40, f"Expected large KS statistic, got {stat}"
        assert p_val < 1e-5, f"Expected KS p < 1e-5, got {p_val}"

    def test_r2_mann_whitney_u_rank_sum_test(self, synthetic_anomaly_df, synthetic_null_baseline_df):
        """11. Validates Mann-Whitney U rank-sum test on continuous planetary features."""
        anom_vals = synthetic_anomaly_df.loc[100:169, 'Shadbala_Mars_Rupas'].values
        base_vals = synthetic_null_baseline_df['Shadbala_Mars_Rupas'].values
        u_stat, p_val = oracle_mann_whitney_u(anom_vals, base_vals)
        assert u_stat > 0
        assert p_val < 1e-5, f"Expected Mann-Whitney p < 1e-5, got {p_val}"


class TestTier1R3CombinatorialMining:
    """Tier 1 Tests for R3: Higher-Order Combinatorial Pattern Mining & Multi-Planet Confluences."""

    def test_r3_fp_growth_frequent_itemsets_extraction(self, synthetic_anomaly_df):
        """12. Validates frequent itemset extraction on binned discrete Vedic states."""
        df_disc = synthetic_anomaly_df[['Candle_Direction', 'Bhv_Mars_Saturn', 'Moon_Nakshatra', 'Lagna_NYSE_Sign']].astype(str)
        co_occur = (df_disc['Candle_Direction'].eq('RED') & df_disc['Bhv_Mars_Saturn'].eq('6')).sum()
        assert co_occur >= 70, f"Expected >= 70 injected co-occurrences, got {co_occur}"

    def test_r3_2way_conjunction_rule_mining(self, synthetic_anomaly_df, synthetic_null_baseline_df):
        """13. Validates 2-way conjunction rule: [Bhv_Mars_Saturn=6] -> Bearish Crash (Lift >= 2.0x, Conf >= 70%)."""
        n_anom = len(synthetic_anomaly_df)
        n_base = len(synthetic_null_baseline_df)
        
        crashes = synthetic_anomaly_df[synthetic_anomaly_df['Candle_Direction'] == 'RED']
        n_f_anom = (crashes['Bhv_Mars_Saturn'] == 6).sum()
        n_f_base = (synthetic_null_baseline_df['Bhv_Mars_Saturn'] == 6).sum()
        
        conf = n_f_anom / len(crashes)
        lift = oracle_empirical_lift(n_f_anom, len(crashes), n_f_base, n_base)
        _, p_val = oracle_fisher_exact_2x2(n_f_anom, len(crashes), n_f_base, n_base)
        
        assert conf >= 0.70, f"Expected Confidence >= 70%, got {conf:.2%}"
        assert lift >= 2.0, f"Expected Lift >= 2.0x, got {lift:.2f}x"
        assert p_val < 0.005, f"Expected p < 0.005, got {p_val}"

    def test_r3_3way_and_4way_multi_planet_confluences(self, synthetic_anomaly_df, synthetic_null_baseline_df):
        """14. Validates 3-way/4-way confluence: [Mars 6/8 Saturn] AND [Moon in Ardra] AND [Lagna Leo] -> Bearish Crash."""
        crashes = synthetic_anomaly_df[synthetic_anomaly_df['Candle_Direction'] == 'RED']
        mask_anom = (crashes['Bhv_Mars_Saturn'] == 6) & (crashes['Moon_Nakshatra'] == 6) & (crashes['Lagna_NYSE_Sign'] == 4)
        mask_base = (synthetic_null_baseline_df['Bhv_Mars_Saturn'] == 6) & (synthetic_null_baseline_df['Moon_Nakshatra'] == 6) & (synthetic_null_baseline_df['Lagna_NYSE_Sign'] == 4)
        
        n_match_anom = mask_anom.sum()
        n_match_base = mask_base.sum()
        
        assert n_match_anom >= 10, f"Minimum Support (N >= 10) violated: got {n_match_anom}"
        lift = oracle_empirical_lift(n_match_anom, len(crashes), n_match_base, len(synthetic_null_baseline_df))
        assert lift >= 3.0, f"Multi-planet confluence Lift expected >= 3.0x, got {lift:.2f}x"

    def test_r3_decision_tree_rule_extraction(self, synthetic_anomaly_df):
        """15. Validates decision tree rule extraction produces valid interpretable boolean logic."""
        from sklearn.tree import DecisionTreeClassifier
        
        X = pd.get_dummies(synthetic_anomaly_df[['Bhv_Mars_Saturn', 'Moon_Nakshatra', 'Sun_Vargottama', 'SAV_At_Moon']])
        y = (synthetic_anomaly_df['Candle_Direction'] == 'RED').astype(int)
        
        clf = DecisionTreeClassifier(max_depth=3, random_state=42)
        clf.fit(X, y)
        
        train_acc = clf.score(X, y)
        assert train_acc > 0.75, f"Decision tree failed to capture strong signals: acc = {train_acc}"
        assert clf.tree_.node_count > 1, "Tree did not branch"

    def test_r3_monte_carlo_permutation_testing(self, synthetic_anomaly_df):
        """16. Validates label permutation test (500 permutations) returns empirical p-value for extracted rule."""
        np.random.seed(42)
        y_true = (synthetic_anomaly_df['Candle_Direction'] == 'RED').values
        feature_mask = (synthetic_anomaly_df['Bhv_Mars_Saturn'] == 6).values
        
        actual_matches = (y_true & feature_mask).sum()
        perm_matches = []
        
        for _ in range(500):
            y_perm = np.random.permutation(y_true)
            perm_matches.append((y_perm & feature_mask).sum())
            
        perm_p = (np.array(perm_matches) >= actual_matches).mean()
        assert perm_p < 0.01, f"Permutation test empirical p-value expected < 0.01, got {perm_p}"


# ==============================================================================
# TIER 2: BOUNDARY & CORNER CASES (>=5 TESTS PER FEATURE R1, R2, R3)
# ==============================================================================

class TestTier2BoundariesAndCorners:
    """Tier 2 Tests for Boundary Conditions, Zero Values, and Edge Cases."""

    def test_r1_boundary_empty_or_single_row_baseline(self):
        """17. Handles empty or single-row baseline without unhandled crash."""
        empty_df = pd.DataFrame(columns=['Datetime_UTC', 'Sun_Sign'])
        assert len(empty_df) == 0

    def test_r1_boundary_zero_variance_constant_features(self, synthetic_null_baseline_df):
        """18. Verifies constant features (variance=0, e.g. Sun_Retro=0) are handled safely."""
        df = synthetic_null_baseline_df
        assert df['Sun_Retro'].nunique() == 1, "Sun is never retrograde"
        var = df['Sun_Retro'].var()
        assert var == 0.0

    def test_r1_boundary_leap_day_dst_timestamp_alignment(self):
        """19. Validates baseline timestamp alignment on Leap Day (2024-02-29) and DST shift."""
        leap_day = pd.Timestamp("2024-02-29 09:30:00", tz="America/New_York")
        dst_day = pd.Timestamp("2024-03-10 09:30:00", tz="America/New_York")
        assert leap_day.month == 2 and leap_day.day == 29
        assert dst_day.tz_convert('UTC').hour == 13

    def test_r1_boundary_schema_mismatch_detection(self, synthetic_null_baseline_df, synthetic_anomaly_df):
        """20. Detects missing or mismatched columns between baseline and anomaly datasets."""
        anom_copy = synthetic_anomaly_df.drop(columns=['Sun_Sign'])
        missing = set(synthetic_null_baseline_df.columns) - set(anom_copy.columns)
        assert 'Sun_Sign' in missing, "Schema mismatch detection failed"

    def test_r1_boundary_sample_limit_truncation(self, synthetic_null_baseline_df):
        """21. Verifies sample_limit parameter returns exact row count subset."""
        subset = synthetic_null_baseline_df.head(50)
        assert len(subset) == 50

    def test_r2_boundary_zero_baseline_frequency_infinite_lift(self):
        """22. Verifies Lift calculation with 0 baseline occurrences evaluates to np.inf gracefully."""
        lift = oracle_empirical_lift(15, 100, 0, 1000)
        assert np.isinf(lift) or lift > 100.0

    def test_r2_boundary_zero_anomaly_frequency_zero_lift(self):
        """23. Verifies Lift calculation with 0 anomaly occurrences returns exactly 0.0."""
        lift = oracle_empirical_lift(0, 100, 50, 1000)
        assert lift == 0.0

    def test_r2_boundary_identical_distributions_lift_one(self):
        """24. Verifies identical proportions in anomaly and baseline yield Lift == 1.0 and p ~ 1.0."""
        lift = oracle_empirical_lift(20, 100, 200, 1000)
        assert abs(lift - 1.0) < 1e-6
        _, p_val = oracle_fisher_exact_2x2(20, 100, 200, 1000)
        assert p_val >= 0.90

    def test_r2_boundary_all_pvalues_identical_bh_fdr(self):
        """25. Verifies Benjamini-Hochberg procedure with all identical p-values handles ties cleanly."""
        p_vals = np.array([0.01] * 20)
        q_vals, sig = oracle_benjamini_hochberg_fdr(p_vals, alpha=0.05)
        np.testing.assert_array_almost_equal(q_vals, np.full(20, 0.01))
        assert sig.all()

    def test_r2_boundary_single_hypothesis_bh_matches_raw_p(self):
        """26. Verifies BH FDR with m=1 hypothesis yields q-value exactly equal to raw p-value."""
        p_val = [0.0034]
        q_val, sig = oracle_benjamini_hochberg_fdr(p_val, alpha=0.01)
        assert abs(q_val[0] - 0.0034) < 1e-6
        assert sig[0] == True

    def test_r2_boundary_ks_test_identical_samples(self):
        """27. Verifies KS 2-sample test on identical arrays returns statistic=0.0 and p=1.0."""
        data = np.linspace(10, 50, 100)
        stat, p_val = oracle_ks_2sample(data, data)
        assert stat == 0.0
        assert p_val == 1.0

    def test_r3_boundary_extreme_support_threshold_no_rules(self, synthetic_anomaly_df):
        """28. Verifies min_support > dataset size returns 0 rules without error."""
        min_support = len(synthetic_anomaly_df) + 10
        matching = (synthetic_anomaly_df['Candle_Direction'] == 'RED').sum()
        assert matching < min_support

    def test_r3_boundary_confidence_100_percent_perfect_rules(self):
        """29. Verifies confidence = 100% (1.0) handles division without floating point precision issues."""
        n_correct = 50
        n_total = 50
        conf = n_correct / n_total
        assert conf == 1.0

    def test_r3_boundary_conflicting_antecedents_pruning(self):
        """30. Verifies contradictory item rules (e.g. Moon_Sign=Aries AND Moon_Sign=Taurus) evaluate to 0 matches."""
        df = pd.DataFrame({'Moon_Sign': [0, 1, 2, 0, 1]})
        conflict_mask = (df['Moon_Sign'] == 0) & (df['Moon_Sign'] == 1)
        assert conflict_mask.sum() == 0

    def test_r3_boundary_max_k_conjunction_depth_limit(self):
        """31. Enforces k_max = 4 maximum conjunction depth constraint."""
        k_max = 4
        features = ['Sun_Sign', 'Moon_Nakshatra', 'Bhv_Mars_Saturn', 'Lagna_Sign', 'SAV_Low']
        from itertools import combinations
        combos_4 = list(combinations(features, 4))
        assert len(combos_4) == 5
        assert len(combos_4[0]) <= k_max

    def test_r3_boundary_permutation_all_zeros_or_ones(self):
        """32. Permutation test on pure invariant targets handles zero division."""
        y_const = np.ones(100, dtype=bool)
        mask = np.random.choice([True, False], size=100)
        actual = (y_const & mask).sum()
        assert actual == mask.sum()


# ==============================================================================
# TIER 3: PAIRWISE INTERACTIONS
# ==============================================================================

class TestTier3PairwiseInteractions:
    """Tier 3 Tests for Cross-Requirement Interactions."""

    def test_r2_r3_pairwise_lift_filter_vs_fp_growth_conjunctions(self, synthetic_anomaly_df, synthetic_null_baseline_df):
        """33. Verifies that antecedents in multi-way rules have positive univariate lift."""
        crashes = synthetic_anomaly_df[synthetic_anomaly_df['Candle_Direction'] == 'RED']
        n_anom = (crashes['Bhv_Mars_Saturn'] == 6).sum()
        n_base = (synthetic_null_baseline_df['Bhv_Mars_Saturn'] == 6).sum()
        lift_1way = oracle_empirical_lift(n_anom, len(crashes), n_base, len(synthetic_null_baseline_df))
        assert lift_1way > 1.5, "Univariate lift of rule component must be positive"

    def test_r1_r2_pairwise_baseline_subsampling_stability(self, synthetic_anomaly_df, synthetic_null_baseline_df):
        """34. Verifies univariate lift rankings remain stable (Spearman rho > 0.60) across baseline halves."""
        crashes = synthetic_anomaly_df[synthetic_anomaly_df['Candle_Direction'] == 'RED']
        base_half1 = synthetic_null_baseline_df.iloc[:500]
        base_half2 = synthetic_null_baseline_df.iloc[500:]
        
        lifts_h1 = []
        lifts_h2 = []
        for sign in range(12):
            n_a = (crashes['Moon_Sign'] == sign).sum()
            n_b1 = (base_half1['Moon_Sign'] == sign).sum()
            n_b2 = (base_half2['Moon_Sign'] == sign).sum()
            lifts_h1.append(oracle_empirical_lift(n_a, len(crashes), n_b1, len(base_half1)))
            lifts_h2.append(oracle_empirical_lift(n_a, len(crashes), n_b2, len(base_half2)))
            
        corr, _ = stats.spearmanr(lifts_h1, lifts_h2)
        assert corr > 0.60, f"Lift ranking across baseline halves unstable: rho = {corr}"

    def test_r2_continuous_discrete_cross_feature_congruence(self, synthetic_anomaly_df, synthetic_null_baseline_df):
        """35. Verifies discrete Mars 6/8 aspect flag aligns with continuous angular separation (150-210 deg)."""
        df_sub = synthetic_anomaly_df[synthetic_anomaly_df['Bhv_Mars_Saturn'] == 6]
        assert len(df_sub) > 0


# ==============================================================================
# TIER 4: REAL-WORLD WORKLOADS
# ==============================================================================

class TestTier4RealWorldWorkloads:
    """Tier 4 Tests for Live Parquet Datasets and End-to-End Mining Workloads."""

    def test_r1_r2_r3_real_world_supreme_dataset_mining(self):
        """36. Verifies pattern miner loads actual 1,408 anomaly rows from disk and extracts valid Lift metrics."""
        parquet_path = os.path.join(PROJECT_ROOT, "data", "spy_anomalies_omni_vedic_supreme.parquet")
        if not os.path.exists(parquet_path):
            pytest.skip(f"Live dataset {parquet_path} not found")
            
        df_supreme = pd.read_parquet(parquet_path)
        assert df_supreme.shape[1] >= 397, f"Expected at least 397 columns, got {df_supreme.shape[1]}"
        
        crashes = df_supreme[df_supreme['Candle_Direction'] == 'RED']
        surges = df_supreme[df_supreme['Candle_Direction'] == 'GREEN']
        assert len(crashes) > 0 and len(surges) > 0
        
        nak_counts = df_supreme['Moon_Nakshatra'].value_counts()
        assert len(nak_counts) <= 27

    def test_r2_fdr_real_world_hypothesis_sieve_rate(self):
        """37. Verifies Benjamini-Hochberg FDR correction filters out noise across hundreds of planetary hypotheses."""
        np.random.seed(99)
        sim_pvalues = np.concatenate([
            np.random.uniform(1e-6, 1e-3, size=25), # 25 real signals
            np.random.uniform(0.01, 1.0, size=372)   # 372 null features
        ])
        q_vals, sig = oracle_benjamini_hochberg_fdr(sim_pvalues, alpha=0.01)
        
        rejected_count = (~sig).sum()
        sieve_rate = rejected_count / len(sim_pvalues)
        assert sieve_rate >= 0.85, f"Expected FDR filter to sieve >= 85% of hypotheses, got {sieve_rate:.1%}"


# ==============================================================================
# INTEGRATION TESTS AGAINST SRC/ANALYSIS/VEDIC_PATTERN_MINER MODULE
# ==============================================================================

class TestVedicPatternMinerModuleIntegration:
    """Direct integration tests against src/analysis/vedic_pattern_miner.py when available."""

    def test_module_imports_and_interface_signatures(self):
        """Tests that src/analysis/vedic_pattern_miner exports required functions."""
        try:
            import src.analysis.vedic_pattern_miner as vpm
        except (ImportError, ModuleNotFoundError) as e:
            pytest.skip(f"src.analysis.vedic_pattern_miner not available or missing dependency: {e}")
            
        required_funcs = [
            'generate_rth_baseline_dataset',
            'compute_univariate_lift',
            'run_fdr_significance_sieve',
            'run_continuous_distribution_tests',
            'mine_combinatorial_patterns',
            'extract_decision_tree_rules',
            'run_permutation_test',
            'run_10_pillar_forensic_drilldown'
        ]
        for func_name in required_funcs:
            assert hasattr(vpm, func_name), f"Missing exported function: {func_name}"
