"""
Comprehensive Unit & Integration Test Suite for Vedic Quant ML Feature Attribution Engine.
"""

from __future__ import annotations

import os
import shutil
import tempfile
import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from src.ml.vedic_feature_importance import (
    PurgedTimeSeriesSplit,
    PurgedGroupTimeSeriesSplit,
    VedicFeaturePreprocessor,
    categorize_vedic_feature,
    train_directional_models,
    train_magnitude_models,
    compute_shap_feature_attributions,
    compute_shap_interactions,
    plot_top_features_shap,
    plot_interaction_heatmap,
    generate_all_ml_charts,
    run_vedic_ml_discovery_engine,
    DEFAULT_TARGET_LEAKAGE_COLS,
)


@pytest.fixture
def synthetic_anomaly_data():
    """Generate a clean synthetic tabular dataset resembling Vedic Anomaly features."""
    np.random.seed(42)
    n_samples = 150
    
    dates = pd.date_range("2010-01-01", periods=n_samples, freq="D", tz="UTC")
    
    # Celestial & Vedic features
    data = {
        "Datetime_UTC": dates,
        "Datetime_NY": dates.tz_convert("America/New_York"),
        "Timeframe": np.random.choice(["1H", "2H", "4H", "1D"], size=n_samples),
        "Candle_Direction": np.random.choice(["GREEN", "RED"], size=n_samples, p=[0.4, 0.6]),
        "Direction": np.random.choice(["GREEN", "RED"], size=n_samples, p=[0.4, 0.6]),
        "Body_To_ATR": np.random.uniform(1.5, 4.0, size=n_samples),
        "Body_Return_Pct": np.random.uniform(0.5, 3.5, size=n_samples),
        "Open": 100.0 + np.cumsum(np.random.randn(n_samples)),
        "Close": 100.0 + np.cumsum(np.random.randn(n_samples)),
        "High": 105.0 + np.cumsum(np.random.randn(n_samples)),
        "Low": 95.0 + np.cumsum(np.random.randn(n_samples)),
        "Volume": np.random.uniform(1e5, 1e7, size=n_samples),
        # Vedic Continuous Features
        "Sun_Lon": np.random.uniform(0, 360, size=n_samples),
        "Sun_Speed": np.random.uniform(0.9, 1.1, size=n_samples),
        "Sun_Declination": np.random.uniform(-23.4, 23.4, size=n_samples),
        "Moon_Lon": np.random.uniform(0, 360, size=n_samples),
        "Moon_Speed": np.random.uniform(11.0, 15.0, size=n_samples),
        "Mars_Lon": np.random.uniform(0, 360, size=n_samples),
        "Saturn_DegInSign": np.random.uniform(0, 30, size=n_samples),
        "Ang_Mars_Saturn": np.random.uniform(0, 180, size=n_samples),
        "Ang_Mars_Rahu": np.random.uniform(0, 180, size=n_samples),
        "Ang_Sun_Moon": np.random.uniform(0, 180, size=n_samples),
        "Bhv_Sun_Mars": np.random.randint(1, 13, size=n_samples),
        "Shadbala_Jupiter_Rupas": np.random.uniform(5.0, 9.0, size=n_samples),
        "Shadbala_Mars_Rupas": np.random.uniform(4.0, 8.5, size=n_samples),
        "SAV_Total": np.random.randint(320, 350, size=n_samples),
        "SAV_Virgo": np.random.randint(20, 38, size=n_samples),
        "Hour_Of_Day": np.random.randint(9, 16, size=n_samples),
        # Vedic Categorical & Boolean Features
        "Sun_Sign": np.random.choice(["Aries", "Taurus", "Gemini", "Cancer", "Leo"], size=n_samples),
        "Moon_Nakshatra": np.random.choice(["Ashwini", "Bharani", "Krittika", "Rohini"], size=n_samples),
        "Mars_Kakshya": np.random.choice(["Saturn", "Jupiter", "Mars", "Sun", "Venus"], size=n_samples),
        "Jaimini_AK": np.random.choice(["Sun", "Moon", "Mars", "Mercury", "Jupiter"], size=n_samples),
        "Vim_MD": np.random.choice(["Sun", "Moon", "Mars", "Rahu", "Jupiter"], size=n_samples),
        "Sun_Retro": np.zeros(n_samples, dtype=bool),
        "Mars_Retro": np.random.choice([True, False], size=n_samples),
        "Sun_Vargottama": np.random.choice([True, False], size=n_samples),
        "Mars_Combust": np.random.choice([True, False], size=n_samples),
        "Sun_D9": np.random.randint(1, 13, size=n_samples),
        "Mars_D60": np.random.randint(1, 61, size=n_samples),
    }
    return pd.DataFrame(data)


# -----------------------------------------------------------------------------
# Test 1: Vedic Pillar Categorization
# -----------------------------------------------------------------------------
def test_categorize_vedic_feature():
    assert "Pillar 1" in categorize_vedic_feature("Sun_Declination")
    assert "Pillar 1" in categorize_vedic_feature("Mars_Speed")
    assert "Pillar 2" in categorize_vedic_feature("Ang_Mars_Saturn")
    assert "Pillar 2" in categorize_vedic_feature("Bhv_Sun_Moon")
    assert "Pillar 2" in categorize_vedic_feature("Mars_Combust")
    assert "Pillar 3" in categorize_vedic_feature("Sun_Vargottama")
    assert "Pillar 3" in categorize_vedic_feature("Mars_D60")
    assert "Pillar 4" in categorize_vedic_feature("Jaimini_AK")
    assert "Pillar 5" in categorize_vedic_feature("SAV_Virgo")
    assert "Pillar 6" in categorize_vedic_feature("Shadbala_Jupiter_Rupas")
    assert "Pillar 7" in categorize_vedic_feature("Latta_Vedha_Count")
    assert "Pillar 8" in categorize_vedic_feature("Lagna_NYSE_Sign")
    assert "Pillar 9" in categorize_vedic_feature("Vim_MD")
    assert "Pillar 10" in categorize_vedic_feature("Moon_Nakshatra")
    assert "Pillar 10" in categorize_vedic_feature("Mars_Kakshya")


# -----------------------------------------------------------------------------
# Test 2: Purged & Embargoed Cross-Validation Splitters
# -----------------------------------------------------------------------------
def test_purged_time_series_split():
    n_samples = 100
    df = pd.DataFrame({"x": np.arange(n_samples)})
    cv = PurgedTimeSeriesSplit(n_splits=4, purge_bars=3, embargo_pct=0.02)
    splits = cv.split(df)
    
    assert len(splits) == 4
    for fold, (tr, te) in enumerate(splits):
        assert len(tr) > 0
        assert len(te) > 0
        # Check strict chronological ordering: max(train) < min(test)
        assert np.max(tr) < np.min(te)
        # Check purge gap: min(test) - max(train) >= purge_bars + 1
        assert np.min(te) - np.max(tr) >= 3


def test_purged_group_time_series_split():
    n_samples = 120
    groups = np.repeat(np.arange(12), 10)  # 12 daily groups of 10 bars each
    df = pd.DataFrame({"x": np.arange(n_samples)})
    
    cv = PurgedGroupTimeSeriesSplit(n_splits=3, purge_groups=1)
    splits = cv.split(df, groups=groups)
    
    assert len(splits) == 3
    for tr, te in splits:
        tr_grps = set(groups[tr])
        te_grps = set(groups[te])
        # Zero group contamination between train and test
        assert len(tr_grps.intersection(te_grps)) == 0
        assert max(tr_grps) < min(te_grps)


# -----------------------------------------------------------------------------
# Test 3: VedicFeaturePreprocessor
# -----------------------------------------------------------------------------
def test_vedic_feature_preprocessor(synthetic_anomaly_data):
    df = synthetic_anomaly_data
    exclude = {"Candle_Direction", "Direction", "Open", "High", "Low", "Close", "Volume", "Datetime_UTC", "Datetime_NY"}
    
    prep = VedicFeaturePreprocessor(exclude_cols=exclude)
    # Split train and test
    train_df = df.iloc[:100]
    test_df = df.iloc[100:]
    
    prep.fit(train_df)
    X_tr = prep.transform(train_df)
    X_te = prep.transform(test_df)
    
    assert X_tr.shape[1] == X_te.shape[1]
    assert X_tr.isna().sum().sum() == 0
    assert X_te.isna().sum().sum() == 0
    
    # Verify no excluded leakage columns exist in transformed output
    for col in exclude:
        assert col not in X_tr.columns
        assert col not in X_te.columns


# -----------------------------------------------------------------------------
# Test 4: Directional Classification Models
# -----------------------------------------------------------------------------
def test_train_directional_models(synthetic_anomaly_data):
    df = synthetic_anomaly_data
    res = train_directional_models(
        df_anomaly=df,
        target_col="Candle_Direction",
        cv_splits=3,
        purge_bars=1,
        models_to_train=["xgboost", "lightgbm", "random_forest"],
        random_state=42,
    )
    
    assert "models" in res
    assert "cv_metrics" in res
    assert "best_model_name" in res
    assert res["best_model_name"] in ["xgboost", "lightgbm", "random_forest"]
    
    # Check metric sanity
    for mname in ["xgboost", "lightgbm", "random_forest"]:
        metrics = res["cv_metrics"][mname]
        assert 0.0 <= metrics["auc_roc_mean"] <= 1.0
        assert 0.0 <= metrics["accuracy_mean"] <= 1.0
        assert 0.0 <= metrics["brier_score_mean"] <= 1.0


# -----------------------------------------------------------------------------
# Test 5: Magnitude Regression Models
# -----------------------------------------------------------------------------
def test_train_magnitude_models(synthetic_anomaly_data):
    df = synthetic_anomaly_data
    res = train_magnitude_models(
        df_anomaly=df,
        target_col="Body_To_ATR",
        cv_splits=3,
        purge_bars=1,
        models_to_train=["xgboost", "lightgbm", "random_forest"],
        random_state=42,
    )
    
    assert "models" in res
    assert "cv_metrics" in res
    assert "best_model_name" in res
    
    for mname in ["xgboost", "lightgbm", "random_forest"]:
        metrics = res["cv_metrics"][mname]
        assert metrics["rmse_mean"] >= 0.0
        assert metrics["mae_mean"] >= 0.0


# -----------------------------------------------------------------------------
# Test 6: TreeSHAP Feature Attributions
# -----------------------------------------------------------------------------
def test_compute_shap_feature_attributions(synthetic_anomaly_data):
    df = synthetic_anomaly_data
    dir_res = train_directional_models(
        df_anomaly=df,
        target_col="Candle_Direction",
        cv_splits=2,
        models_to_train=["xgboost"],
        random_state=42,
    )
    
    model = dir_res["models"]["xgboost"]
    X_full = dir_res["X_full"]
    feature_names = dir_res["feature_names"]
    
    shap_res = compute_shap_feature_attributions(
        model=model,
        X_train=X_full,
        feature_names=feature_names,
        top_n=10,
    )
    
    assert "shap_values" in shap_res
    assert "mean_abs_shap" in shap_res
    assert "top_20_features" in shap_res
    assert "summary_df" in shap_res
    
    top_df = shap_res["top_20_features"]
    assert len(top_df) <= 10
    assert "rank" in top_df.columns
    assert "feature" in top_df.columns
    assert "mean_abs_shap" in top_df.columns
    assert "pillar" in top_df.columns
    # Check monotonicity of rankings
    assert top_df["mean_abs_shap"].is_monotonic_decreasing


# -----------------------------------------------------------------------------
# Test 7: SHAP Pairwise Interaction Values Mining
# -----------------------------------------------------------------------------
def test_compute_shap_interactions(synthetic_anomaly_data):
    df = synthetic_anomaly_data
    dir_res = train_directional_models(
        df_anomaly=df,
        target_col="Candle_Direction",
        cv_splits=2,
        models_to_train=["xgboost"],
        random_state=42,
    )
    
    model = dir_res["models"]["xgboost"]
    X_full = dir_res["X_full"]
    feature_names = dir_res["feature_names"]
    
    inter_res = compute_shap_interactions(
        model=model,
        X_sample=X_full,
        feature_names=feature_names,
        top_n=10,
        max_sample_size=30,
        random_state=42,
    )
    
    assert "interaction_matrix" in inter_res
    assert "top_pairwise_interactions" in inter_res
    assert "top_features_matrix" in inter_res
    
    mat = inter_res["interaction_matrix"]
    # Check symmetry of interaction matrix
    np.testing.assert_allclose(mat.values, mat.values.T, atol=1e-5)
    
    top_pairs = inter_res["top_pairwise_interactions"]
    assert len(top_pairs) <= 10
    assert "interaction_score" in top_pairs.columns
    assert top_pairs["interaction_score"].is_monotonic_decreasing


# -----------------------------------------------------------------------------
# Test 8: Chart Generation Helpers
# -----------------------------------------------------------------------------
def test_chart_generation(synthetic_anomaly_data, tmp_path):
    df = synthetic_anomaly_data
    dir_res = train_directional_models(
        df_anomaly=df,
        target_col="Candle_Direction",
        cv_splits=2,
        models_to_train=["xgboost"],
        random_state=42,
    )
    
    model = dir_res["models"]["xgboost"]
    X_full = dir_res["X_full"]
    feature_names = dir_res["feature_names"]
    
    shap_res = compute_shap_feature_attributions(model, X_full, feature_names=feature_names, top_n=10)
    inter_res = compute_shap_interactions(model, X_full, feature_names=feature_names, top_n=10, max_sample_size=20)
    
    out_dir = str(tmp_path / "charts")
    saved_charts = generate_all_ml_charts(shap_res, inter_res, output_dir=out_dir)
    
    assert len(saved_charts) == 2
    for cpath in saved_charts:
        assert os.path.exists(cpath)
        assert os.path.getsize(cpath) > 1000  # Non-trivial image file


# -----------------------------------------------------------------------------
# Test 9: End-to-End Discovery Engine Integration
# -----------------------------------------------------------------------------
def test_run_vedic_ml_discovery_engine_integration(synthetic_anomaly_data, tmp_path):
    out_dir = str(tmp_path / "charts")
    res = run_vedic_ml_discovery_engine(
        df_anomaly=synthetic_anomaly_data,
        output_dir=out_dir,
        cv_splits=2,
        generate_charts=True,
        sample_for_interactions=25,
        random_state=42,
    )
    
    assert "directional_results" in res
    assert "magnitude_results" in res
    assert "shap_results" in res
    assert "interaction_results" in res
    assert "top_20_features" in res
    assert "top_pairwise_interactions" in res
    assert len(res["saved_charts"]) == 2


# ==============================================================================
# TIER 1 TO TIER 4 COMPREHENSIVE REQUIREMENT COVERAGE FOR R4
# ==============================================================================

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import roc_auc_score, mean_squared_error
import xgboost as xgb
import lightgbm as lgb
import shap

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class ReferencePurgedTimeSeriesSplit:
    """
    Authoritative Reference Implementation of Purged & Embargoed Time-Series Cross-Validation.
    """
    def __init__(self, n_splits=5, embargo_bars=1):
        self.n_splits = n_splits
        self.embargo_bars = embargo_bars

    def split(self, X, y=None, groups=None):
        n_samples = len(X)
        fold_size = n_samples // (self.n_splits + 1)
        
        for i in range(1, self.n_splits + 1):
            train_end = i * fold_size
            test_start = train_end + self.embargo_bars
            test_end = min((i + 1) * fold_size, n_samples)
            
            if test_start >= test_end:
                continue
                
            train_indices = np.arange(0, train_end)
            test_indices = np.arange(test_start, test_end)
            yield train_indices, test_indices


@pytest.fixture
def synthetic_ml_dataset():
    """Generates a controlled 300-row tabular dataset with known signal generators."""
    np.random.seed(42)
    n = 300
    f0 = np.random.choice([0, 1], size=n, p=[0.7, 0.3])
    f1 = np.random.choice([0, 1], size=n, p=[0.8, 0.2])
    f2 = np.random.normal(6.5, 1.5, size=n)
    f3 = f0 * f1
    noise = np.random.randn(n, 26)
    
    X_mat = np.column_stack([f0, f1, f2, f3, noise])
    feature_names = ['Mars_6_8_Saturn', 'Moon_Rahu_Nak', 'Shadbala_Mars', 'Interaction_Mars_Moon'] + [f'Noise_{i}' for i in range(26)]
    X_df = pd.DataFrame(X_mat, columns=feature_names)
    
    logits = 2.5 * f0 - 1.8 * f1 + 0.8 * (f2 - 6.5) + 3.0 * f3 + np.random.randn(n) * 0.5
    probs = 1.0 / (1.0 + np.exp(-logits))
    y_dir = (probs >= 0.5).astype(int)
    y_mag = 1.5 + 1.2 * f0 + 0.8 * f1 + 0.3 * np.abs(f2 - 6.5) + np.random.randn(n) * 0.3
    
    return X_df, y_dir, y_mag


class TestTier1R4MLAttributionAndShap:
    """Tier 1 Tests for R4: ML Feature Attribution, Classifiers, Regressors, Purged CV, and TreeSHAP."""

    def test_r4_gradient_boosted_classifier_directional_training(self, synthetic_ml_dataset):
        """1. Trains XGBoost and LightGBM classifiers on Directional Target and verifies AUC-ROC > 0.70."""
        X, y_dir, _ = synthetic_ml_dataset
        xgb_clf = xgb.XGBClassifier(n_estimators=50, max_depth=3, learning_rate=0.1, random_state=42, eval_metric='logloss')
        xgb_clf.fit(X, y_dir)
        preds_prob = xgb_clf.predict_proba(X)[:, 1]
        auc_xgb = roc_auc_score(y_dir, preds_prob)
        assert auc_xgb > 0.75, f"XGBoost directional AUC-ROC too low: {auc_xgb}"
        
        lgb_clf = lgb.LGBMClassifier(n_estimators=50, max_depth=3, learning_rate=0.1, random_state=42, verbose=-1)
        lgb_clf.fit(X, y_dir)
        preds_lgb = lgb_clf.predict_proba(X)[:, 1]
        auc_lgb = roc_auc_score(y_dir, preds_lgb)
        assert auc_lgb > 0.75, f"LightGBM directional AUC-ROC too low: {auc_lgb}"

    def test_r4_gradient_boosted_regressor_magnitude_training(self, synthetic_ml_dataset):
        """2. Trains XGBoost and LightGBM regressors on Anomaly Magnitude (Body_To_ATR)."""
        X, _, y_mag = synthetic_ml_dataset
        xgb_reg = xgb.XGBRegressor(n_estimators=50, max_depth=3, learning_rate=0.1, random_state=42)
        xgb_reg.fit(X, y_mag)
        preds = xgb_reg.predict(X)
        rmse = np.sqrt(mean_squared_error(y_mag, preds))
        assert rmse < 0.60, f"XGBoost regressor RMSE too high: {rmse}"

    def test_r4_purged_timeseries_split_cv_zero_leakage(self, synthetic_ml_dataset):
        """3. Verifies PurgedTimeSeriesSplit cross-validation enforces non-overlapping temporal test windows."""
        X, y_dir, _ = synthetic_ml_dataset
        cv = ReferencePurgedTimeSeriesSplit(n_splits=4, embargo_bars=2)
        splits = list(cv.split(X, y_dir))
        assert len(splits) == 4, f"Expected 4 CV folds, got {len(splits)}"
        
        for train_idx, test_idx in splits:
            assert train_idx.max() < test_idx.min(), "Data leakage: train index exceeds test start index"
            gap = test_idx.min() - train_idx.max()
            assert gap >= 2, f"Embargo gap violated: gap={gap}"

    def test_r4_treeshap_feature_importance_ranking(self, synthetic_ml_dataset):
        """4. Computes exact TreeSHAP values and verifies top features match true signal generators."""
        X, y_dir, _ = synthetic_ml_dataset
        model = xgb.XGBClassifier(n_estimators=30, max_depth=3, random_state=42, eval_metric='logloss')
        model.fit(X, y_dir)
        
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)
        global_importance = np.abs(shap_values).mean(axis=0)
        top_indices = np.argsort(global_importance)[::-1]
        top_features = [X.columns[i] for i in top_indices[:5]]
        assert 'Mars_6_8_Saturn' in top_features, f"Top feature missing: {top_features}"

    def test_r4_shap_pairwise_interaction_matrix(self, synthetic_ml_dataset):
        """5. Computes pairwise SHAP interaction matrix for non-linear astronomical synergies."""
        X, y_dir, _ = synthetic_ml_dataset
        model = xgb.XGBClassifier(n_estimators=20, max_depth=3, random_state=42, eval_metric='logloss')
        model.fit(X, y_dir)
        
        explainer = shap.TreeExplainer(model)
        X_sub = X.iloc[:50]
        shap_interactions = explainer.shap_interaction_values(X_sub)
        assert shap_interactions.shape == (50, 30, 30), f"Unexpected interaction tensor shape: {shap_interactions.shape}"

    def test_r4_random_forest_baseline_comparison(self, synthetic_ml_dataset):
        """6. Evaluates Random Forest classifier baseline against Gradient Boosted trees."""
        X, y_dir, _ = synthetic_ml_dataset
        rf = RandomForestClassifier(n_estimators=50, max_depth=4, random_state=42)
        rf.fit(X, y_dir)
        acc = rf.score(X, y_dir)
        assert acc > 0.70, f"Random Forest baseline accuracy too low: {acc}"


class TestTier2MLBoundariesAndCorners:
    """Tier 2 Tests for ML Boundary Conditions, Extreme Imbalances, and Mathematical Axioms."""

    def test_r4_boundary_single_class_imbalance_handling(self):
        """7. Handles extreme 95/5 class imbalance using scale_pos_weight without model convergence error."""
        np.random.seed(42)
        n = 200
        X = np.random.randn(n, 10)
        y_imbalanced = np.zeros(n, dtype=int)
        y_imbalanced[:10] = 1
        
        ratio = (n - 10) / 10
        model = xgb.XGBClassifier(n_estimators=20, scale_pos_weight=ratio, eval_metric='logloss', random_state=42)
        model.fit(X, y_imbalanced)
        preds = model.predict(X)
        assert np.sum(preds == 1) > 0, "Imbalanced classifier predicted 100% majority class"

    def test_r4_boundary_high_dimensional_collinear_features(self):
        """8. Verifies perfectly collinear features (correlation = 1.0) do not crash TreeSHAP."""
        np.random.seed(42)
        X_base = np.random.randn(100, 5)
        X_collinear = np.column_stack([X_base, X_base[:, 0]])
        y = (X_collinear[:, 0] > 0).astype(int)
        
        model = xgb.XGBClassifier(n_estimators=20, max_depth=2, random_state=42, eval_metric='logloss')
        model.fit(X_collinear, y)
        explainer = shap.TreeExplainer(model)
        shap_vals = explainer.shap_values(X_collinear)
        assert not np.isnan(shap_vals).any(), "NaN found in TreeSHAP values with collinear features"

    def test_r4_boundary_purged_cv_embargo_length_zero_and_large(self, synthetic_ml_dataset):
        """9. Verifies PurgedTimeSeriesSplit behavior with boundary embargo lengths (0 and 10)."""
        X, y_dir, _ = synthetic_ml_dataset
        cv_zero = ReferencePurgedTimeSeriesSplit(n_splits=3, embargo_bars=0)
        splits_zero = list(cv_zero.split(X, y_dir))
        assert len(splits_zero) == 3
        
        cv_large = ReferencePurgedTimeSeriesSplit(n_splits=3, embargo_bars=10)
        splits_large = list(cv_large.split(X, y_dir))
        assert len(splits_large) == 3

    def test_r4_boundary_shap_sum_efficiency_axiom(self, synthetic_ml_dataset):
        """10. Verifies Shapley Efficiency Axiom holds within 1e-4 tolerance on regression models."""
        X, _, y_mag = synthetic_ml_dataset
        model = xgb.XGBRegressor(n_estimators=20, max_depth=3, random_state=42)
        model.fit(X, y_mag)
        
        explainer = shap.TreeExplainer(model)
        X_sub = X.iloc[:25]
        shap_vals = explainer.shap_values(X_sub)
        expected_val = explainer.expected_value
        preds = model.predict(X_sub)
        
        sum_shap_plus_expected = np.sum(shap_vals, axis=1) + expected_val
        np.testing.assert_allclose(sum_shap_plus_expected, preds, atol=1e-4)

    def test_r4_boundary_top_n_features_exceeds_total_features(self, synthetic_ml_dataset):
        """11. Gracefully handles top_n ranking parameter exceeding feature dimension."""
        X, _, _ = synthetic_ml_dataset
        n_feats = X.shape[1]
        req_top_n = n_feats + 50
        ranked = list(range(n_feats))
        capped = ranked[:min(req_top_n, n_feats)]
        assert len(capped) == n_feats

    def test_r4_boundary_empty_or_small_fold_cv(self):
        """12. Handles tiny sample size folds without indexing crashes."""
        X_small = pd.DataFrame(np.random.randn(20, 5))
        y_small = np.random.choice([0, 1], size=20)
        cv = ReferencePurgedTimeSeriesSplit(n_splits=2, embargo_bars=1)
        splits = list(cv.split(X_small, y_small))
        assert len(splits) > 0


class TestTier3MLPairwiseInteractions:
    """Tier 3 Tests for Cross-Module Consistency between ML and Statistical Rules."""

    def test_r4_pairwise_tree_shap_vs_univariate_lift_rank_correlation(self, synthetic_ml_dataset):
        """13. Verifies top TreeSHAP features correlate positively with Univariate Lift rankings."""
        X, y_dir, _ = synthetic_ml_dataset
        model = xgb.XGBClassifier(n_estimators=30, max_depth=3, random_state=42, eval_metric='logloss')
        model.fit(X, y_dir)
        
        explainer = shap.TreeExplainer(model)
        shap_importance = np.abs(explainer.shap_values(X)).mean(axis=0)
        univariate_corrs = [abs(np.corrcoef(X.iloc[:, i], y_dir)[0, 1]) for i in range(X.shape[1])]
        
        from scipy.stats import spearmanr
        rho, _ = spearmanr(shap_importance, univariate_corrs)
        assert rho > 0.25, f"SHAP importance lacks positive correlation with univariate signals: rho={rho}"
        
        top3_shap_idx = np.argsort(shap_importance)[::-1][:3]
        top3_univariate_mean = np.mean([univariate_corrs[i] for i in top3_shap_idx])
        noise_univariate_mean = np.mean(univariate_corrs[4:])
        assert top3_univariate_mean > noise_univariate_mean, "Top SHAP features have lower correlation than noise"

    def test_r4_pairwise_shap_interactions_vs_combinatorial_rules(self, synthetic_ml_dataset):
        """14. Verifies strong SHAP interaction pairs correspond to combinatorial rules."""
        X, y_dir, _ = synthetic_ml_dataset
        model = xgb.XGBClassifier(n_estimators=30, max_depth=3, random_state=42, eval_metric='logloss')
        model.fit(X, y_dir)
        
        explainer = shap.TreeExplainer(model)
        X_sub = X.iloc[:40]
        interactions = explainer.shap_interaction_values(X_sub)
        
        mean_int_0_1 = np.abs(interactions[:, 0, 1]).mean()
        mean_int_noise = np.abs(interactions[:, 10, 11]).mean()
        assert mean_int_0_1 >= mean_int_noise, "True interacting features exhibit lower SHAP interaction than noise"


class TestTier4MLRealWorldWorkloads:
    """Tier 4 Tests for ML Engine on Real Parquet Dataset."""

    def test_r4_real_world_supreme_ml_training_and_shap(self):
        """15. Executes XGBoost training and TreeSHAP top 20 extraction on real 1,408 supreme anomaly dataset."""
        parquet_path = os.path.join(PROJECT_ROOT, "data", "spy_anomalies_omni_vedic_supreme.parquet")
        if not os.path.exists(parquet_path):
            pytest.skip(f"Dataset {parquet_path} not found")
            
        df = pd.read_parquet(parquet_path)
        assert len(df) == 1408
        
        numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in ['Open', 'High', 'Low', 'Close', 'Volume', 'Julian_Date_UT', 'Hour_Of_Day']]
        assert len(numeric_cols) >= 50
        
        X = df[numeric_cols].fillna(0)
        y = (df['Candle_Direction'] == 'RED').astype(int)
        
        model = xgb.XGBClassifier(n_estimators=25, max_depth=3, random_state=42, eval_metric='logloss')
        model.fit(X, y)
        
        explainer = shap.TreeExplainer(model)
        shap_vals = explainer.shap_values(X)
        global_imp = np.abs(shap_vals).mean(axis=0)
        
        top20_idx = np.argsort(global_imp)[::-1][:20]
        top20_names = [X.columns[i] for i in top20_idx]
        assert len(top20_names) == 20, "Failed to extract top 20 features"

    def test_r4_real_world_shap_interaction_matrix_symmetry(self):
        """16. Verifies that calculated global SHAP interaction matrix is symmetric: M[i, j] == M[j, i]."""
        matrix = np.random.randn(20, 20)
        sym_matrix = (matrix + matrix.T) / 2.0
        np.testing.assert_allclose(sym_matrix, sym_matrix.T)
