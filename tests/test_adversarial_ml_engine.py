import os
import numpy as np
import pandas as pd
import pytest
import shap
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    f1_score,
    mean_absolute_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
    root_mean_squared_error,
)
from scipy.special import expit

from src.ml.vedic_feature_importance import (
    PurgedTimeSeriesSplit,
    PurgedGroupTimeSeriesSplit,
    VedicFeaturePreprocessor,
    categorize_vedic_feature,
    train_directional_models,
    train_magnitude_models,
    compute_shap_feature_attributions,
    compute_shap_interactions,
    generate_all_ml_charts,
    run_vedic_ml_discovery_engine,
    DEFAULT_TARGET_LEAKAGE_COLS,
)

@pytest.fixture
def synthetic_anomaly_data():
    np.random.seed(42)
    n_samples = 120
    dates = pd.date_range("2010-01-01", periods=n_samples, freq="D", tz="UTC")
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

class TestAdversarialDataLeakageAndPurging:
    @pytest.mark.parametrize("n_samples", [17, 53, 100, 250, 1408])
    @pytest.mark.parametrize("n_splits", [2, 3, 5, 7, 10])
    @pytest.mark.parametrize("purge_bars", [0, 1, 2, 5, 15])
    def test_purged_time_series_split_strict_temporal_order(self, n_samples, n_splits, purge_bars):
        if n_samples < (n_splits + 1):
            return
        df = pd.DataFrame({"val": np.arange(n_samples)})
        cv = PurgedTimeSeriesSplit(n_splits=n_splits, purge_bars=purge_bars)
        splits = cv.split(df)

        for fold_idx, (train_idx, test_idx) in enumerate(splits):
            assert len(train_idx) > 0
            assert len(test_idx) > 0
            max_train = int(np.max(train_idx))
            min_test = int(np.min(test_idx))
            assert max_train < min_test
            actual_gap = min_test - max_train
            expected_min_gap = purge_bars + 1
            assert actual_gap >= expected_min_gap
            overlap = set(train_idx).intersection(set(test_idx))
            assert len(overlap) == 0

    @pytest.mark.parametrize("n_splits", [2, 3, 5])
    @pytest.mark.parametrize("purge_groups", [0, 1, 2])
    def test_purged_group_time_series_split_adversarial_groups(self, n_splits, purge_groups):
        group_sizes = [5, 12, 3, 20, 8, 15, 7, 25, 4, 18, 9, 30]
        groups = []
        for g_id, size in enumerate(group_sizes):
            groups.extend([f"group_{g_id:02d}"] * size)
        groups = np.array(groups)
        n_samples = len(groups)
        df = pd.DataFrame({"val": np.arange(n_samples)})

        cv = PurgedGroupTimeSeriesSplit(n_splits=n_splits, purge_groups=purge_groups)
        splits = cv.split(df, groups=groups)

        for fold_idx, (train_idx, test_idx) in enumerate(splits):
            train_grps = set(groups[train_idx])
            test_grps = set(groups[test_idx])
            contamination = train_grps.intersection(test_grps)
            assert len(contamination) == 0
            max_train_grp = max(train_grps)
            min_test_grp = min(test_grps)
            assert max_train_grp < min_test_grp

    def test_supreme_dataset_100_percent_ohlcv_exclusion(self):
        parquet_path = "data/spy_anomalies_omni_vedic_supreme.parquet"
        if not os.path.exists(parquet_path):
            pytest.skip("Dataset not found")
        df = pd.read_parquet(parquet_path)
        
        prep = VedicFeaturePreprocessor()
        prep.fit(df)
        features = set(prep.feature_names_)

        for col in DEFAULT_TARGET_LEAKAGE_COLS:
            assert col not in features, f"LEAKAGE ERROR: Target/Market column {col} in features!"

        assert len(features) == 359

    def test_preprocessor_in_sample_fitting_guarantee(self):
        train_df = pd.DataFrame({
            "Sun_Sign": ["Aries", "Taurus", "Gemini"],
            "Sun_Lon": [10.0, 20.0, np.nan],
            "Sun_Retro": [True, False, True],
            "Candle_Direction": ["GREEN", "RED", "GREEN"],
            "Close": [100.0, 101.0, 102.0],
        })
        test_df = pd.DataFrame({
            "Sun_Sign": ["Aries", "Leo"],
            "Sun_Lon": [np.nan, 80.0],
            "Sun_Retro": [False, True],
            "Candle_Direction": ["RED", "RED"],
            "Close": [103.0, 104.0],
        })
        
        prep = VedicFeaturePreprocessor(exclude_cols=DEFAULT_TARGET_LEAKAGE_COLS)
        prep.fit(train_df)
        
        assert prep.num_medians_["Sun_Lon"] == 15.0
        X_te = prep.transform(test_df)
        assert X_te.loc[0, "Sun_Lon"] == 15.0
        assert X_te.loc[1, "Sun_Sign"] == -1.0
        assert "Close" not in X_te.columns
        assert "Candle_Direction" not in X_te.columns

class TestAdversarialTreeSHAPAxioms:
    @pytest.fixture
    def real_or_synthetic_dataset(self):
        parquet_path = "data/spy_anomalies_omni_vedic_supreme.parquet"
        if os.path.exists(parquet_path):
            df = pd.read_parquet(parquet_path)
        else:
            np.random.seed(42)
            df = pd.DataFrame({
                "Sun_Lon": np.random.uniform(0, 360, 200),
                "Moon_Lon": np.random.uniform(0, 360, 200),
                "Mars_Lon": np.random.uniform(0, 360, 200),
                "Sun_Sign": np.random.choice(["Aries", "Taurus", "Gemini"], 200),
                "Candle_Direction": np.random.choice(["GREEN", "RED"], 200),
                "Body_To_ATR": np.random.uniform(1.5, 4.0, 200),
                "Open": np.random.uniform(100, 200, 200),
                "Close": np.random.uniform(100, 200, 200),
            })
        return df

    def test_shapley_efficiency_axiom_xgboost_regressor(self, real_or_synthetic_dataset):
        res = train_magnitude_models(
            df_anomaly=real_or_synthetic_dataset,
            target_col="Body_To_ATR",
            cv_splits=2,
            models_to_train=["xgboost"],
            random_state=42,
        )
        model = res["models"]["xgboost"]
        X_eval = res["X_full"].iloc[:50]
        
        explainer = shap.TreeExplainer(model)
        shap_vals = explainer.shap_values(X_eval)
        expected_val = explainer.expected_value
        preds = model.predict(X_eval)
        
        shap_sum = np.sum(shap_vals, axis=1) + expected_val
        np.testing.assert_allclose(shap_sum, preds, atol=1e-4)

    def test_shapley_efficiency_axiom_lightgbm_regressor(self, real_or_synthetic_dataset):
        res = train_magnitude_models(
            df_anomaly=real_or_synthetic_dataset,
            target_col="Body_To_ATR",
            cv_splits=2,
            models_to_train=["lightgbm"],
            random_state=42,
        )
        model = res["models"]["lightgbm"]
        X_eval = res["X_full"].iloc[:50]
        
        explainer = shap.TreeExplainer(model)
        shap_vals = explainer.shap_values(X_eval)
        expected_val = explainer.expected_value
        preds = model.predict(X_eval)
        
        shap_sum = np.sum(shap_vals, axis=1) + expected_val
        np.testing.assert_allclose(shap_sum, preds, atol=1e-4)

    def test_shapley_efficiency_axiom_random_forest_regressor(self, real_or_synthetic_dataset):
        res = train_magnitude_models(
            df_anomaly=real_or_synthetic_dataset,
            target_col="Body_To_ATR",
            cv_splits=2,
            models_to_train=["random_forest"],
            random_state=42,
        )
        model = res["models"]["random_forest"]
        X_eval = res["X_full"].iloc[:50]
        
        explainer = shap.TreeExplainer(model)
        shap_vals = explainer.shap_values(X_eval)
        expected_val = explainer.expected_value
        preds = model.predict(X_eval)
        
        shap_sum = np.sum(shap_vals, axis=1) + expected_val
        np.testing.assert_allclose(shap_sum, preds, atol=1e-4)

    def test_shapley_efficiency_axiom_xgboost_classifier(self, real_or_synthetic_dataset):
        res = train_directional_models(
            df_anomaly=real_or_synthetic_dataset,
            target_col="Candle_Direction",
            cv_splits=2,
            models_to_train=["xgboost"],
            random_state=42,
        )
        model = res["models"]["xgboost"]
        X_eval = res["X_full"].iloc[:50]
        
        explainer = shap.TreeExplainer(model)
        shap_vals = explainer.shap_values(X_eval)
        expected_val = explainer.expected_value
        
        margin_from_shap = np.sum(shap_vals, axis=1) + expected_val
        prob_from_shap = expit(margin_from_shap)
        prob_from_model = model.predict_proba(X_eval)[:, 1]
        
        np.testing.assert_allclose(prob_from_shap, prob_from_model, atol=1e-4)

    def test_shap_pairwise_interaction_tensor_symmetry(self, real_or_synthetic_dataset):
        res = train_directional_models(
            df_anomaly=real_or_synthetic_dataset,
            target_col="Candle_Direction",
            cv_splits=2,
            models_to_train=["xgboost"],
            random_state=42,
        )
        model = res["models"]["xgboost"]
        X_eval = res["X_full"].iloc[:30]
        
        explainer = shap.TreeExplainer(model)
        raw_interactions = explainer.shap_interaction_values(X_eval)
        
        for i in range(len(X_eval)):
            sample_matrix = raw_interactions[i]
            np.testing.assert_allclose(sample_matrix, sample_matrix.T, atol=1e-5)

        inter_res = compute_shap_interactions(
            model=model,
            X_sample=res["X_full"],
            feature_names=res["feature_names"],
            top_n=20,
            max_sample_size=30,
            random_state=42,
        )
        mat = inter_res["interaction_matrix"].values
        np.testing.assert_allclose(mat, mat.T, atol=1e-5)

    def test_shap_interaction_marginal_sum_consistency(self, real_or_synthetic_dataset):
        res = train_directional_models(
            df_anomaly=real_or_synthetic_dataset,
            target_col="Candle_Direction",
            cv_splits=2,
            models_to_train=["xgboost"],
            random_state=42,
        )
        model = res["models"]["xgboost"]
        X_eval = res["X_full"].iloc[:20]
        
        explainer = shap.TreeExplainer(model)
        shap_vals = explainer.shap_values(X_eval)
        interactions = explainer.shap_interaction_values(X_eval)
        
        summed_interactions = np.sum(interactions, axis=2)
        np.testing.assert_allclose(summed_interactions, shap_vals, atol=1e-4)

class TestAdversarialOutOfSampleMetrics:
    def test_directional_cv_metrics_mathematical_precision(self, synthetic_anomaly_data):
        res = train_directional_models(
            df_anomaly=synthetic_anomaly_data,
            target_col="Candle_Direction",
            cv_splits=3,
            purge_bars=2,
            models_to_train=["xgboost", "lightgbm", "random_forest"],
            random_state=42,
        )
        
        for mname in ["xgboost", "lightgbm", "random_forest"]:
            cv_info = res["cv_metrics"][mname]
            folds = cv_info["folds"]
            
            for fold in folds:
                f_idx = fold["fold"]
                pred_dict = [p for p in res["cv_predictions"][mname] if p["fold"] == f_idx][0]
                y_true = pred_dict["y_true"]
                y_pred = pred_dict["y_pred"]
                y_prob = pred_dict["y_prob"]
                
                expected_auc = roc_auc_score(y_true, y_prob) if len(np.unique(y_true)) > 1 else 0.5
                expected_acc = accuracy_score(y_true, y_pred)
                expected_f1 = f1_score(y_true, y_pred, zero_division=0)
                expected_prec = precision_score(y_true, y_pred, zero_division=0)
                expected_rec = recall_score(y_true, y_pred, zero_division=0)
                expected_brier = brier_score_loss(y_true, y_prob)
                
                assert np.isclose(fold["auc_roc"], expected_auc, atol=1e-6)
                assert np.isclose(fold["accuracy"], expected_acc, atol=1e-6)
                assert np.isclose(fold["f1"], expected_f1, atol=1e-6)
                assert np.isclose(fold["precision"], expected_prec, atol=1e-6)
                assert np.isclose(fold["recall"], expected_rec, atol=1e-6)
                assert np.isclose(fold["brier_score"], expected_brier, atol=1e-6)

            auc_list = [f["auc_roc"] for f in folds]
            assert np.isclose(cv_info["auc_roc_mean"], np.mean(auc_list), atol=1e-6)

    def test_magnitude_cv_metrics_mathematical_precision(self, synthetic_anomaly_data):
        res = train_magnitude_models(
            df_anomaly=synthetic_anomaly_data,
            target_col="Body_To_ATR",
            cv_splits=3,
            purge_bars=2,
            models_to_train=["xgboost", "lightgbm", "random_forest"],
            random_state=42,
        )
        
        for mname in ["xgboost", "lightgbm", "random_forest"]:
            cv_info = res["cv_metrics"][mname]
            folds = cv_info["folds"]
            
            for fold in folds:
                f_idx = fold["fold"]
                pred_dict = [p for p in res["cv_predictions"][mname] if p["fold"] == f_idx][0]
                y_true = pred_dict["y_true"]
                y_pred = pred_dict["y_pred"]
                
                expected_rmse = root_mean_squared_error(y_true, y_pred)
                expected_mae = mean_absolute_error(y_true, y_pred)
                expected_r2 = r2_score(y_true, y_pred)
                
                assert np.isclose(fold["rmse"], expected_rmse, atol=1e-6)
                assert np.isclose(fold["mae"], expected_mae, atol=1e-6)
                assert np.isclose(fold["r2"], expected_r2, atol=1e-6)

    def test_end_to_end_supreme_engine_execution(self, tmp_path):
        parquet_path = "data/spy_anomalies_omni_vedic_supreme.parquet"
        if not os.path.exists(parquet_path):
            pytest.skip("Dataset not found")
            
        out_dir = str(tmp_path / "reports_charts")
        results = run_vedic_ml_discovery_engine(
            parquet_path=parquet_path,
            output_dir=out_dir,
            cv_splits=3,
            generate_charts=True,
            sample_for_interactions=40,
            random_state=42,
        )
        
        assert "directional_results" in results
        assert "magnitude_results" in results
        assert "shap_results" in results
        assert "interaction_results" in results
        assert "top_20_features" in results
        assert "top_pairwise_interactions" in results
        
        top20 = results["top_20_features"]
        assert len(top20) == 20
        assert list(top20.columns) == ["rank", "feature", "mean_abs_shap", "std_shap", "directional_corr", "pillar", "feature_index"]
        assert top20["mean_abs_shap"].is_monotonic_decreasing
        
        assert len(results["saved_charts"]) == 2
        for p in results["saved_charts"]:
            assert os.path.exists(p)
            assert os.path.getsize(p) > 5000
