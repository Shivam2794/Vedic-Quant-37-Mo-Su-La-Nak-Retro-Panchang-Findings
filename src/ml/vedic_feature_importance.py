"""
Vedic Quant Machine Learning Feature Attribution & Interaction Mining Engine.

This module implements:
1. Model Architectures:
   - XGBoost (XGBClassifier, XGBRegressor)
   - LightGBM (LGBMClassifier, LGBMRegressor)
   - Random Forest (RandomForestClassifier, RandomForestRegressor)
2. Purged & Embargoed Cross-Validation:
   - PurgedTimeSeriesSplit & PurgedGroupTimeSeriesSplit (zero lookahead leakage)
3. TreeSHAP Global Feature Attribution:
   - Exact TreeSHAP feature importance across all Omni-Vedic features
   - Top 20 Global Driver Features extraction by Mean Absolute SHAP value
4. Pairwise SHAP Interaction Mining:
   - Second-order SHAP interaction tensors
   - Structured pairwise interaction matrices and synergy ranking
5. Visualization Export Helpers:
   - High-resolution publication charts in reports/charts/
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import shap
from scipy.stats import pearsonr, spearmanr
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
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
from sklearn.preprocessing import OrdinalEncoder

import lightgbm as lgb
import xgboost as xgb

# -----------------------------------------------------------------------------
# Target Leakage & Market Column Exclusions
# -----------------------------------------------------------------------------
DEFAULT_TARGET_LEAKAGE_COLS: set[str] = {
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "Real_Body",
    "Body",
    "Candle_Range",
    "Range",
    "Upper_Wick",
    "Lower_Wick",
    "Upper_Wick_Ratio",
    "Lower_Wick_Ratio",
    "Solid_Ratio",
    "Max_Wick_Ratio",
    "Candle_Direction",
    "Direction",
    "Body_Return_Pct",
    "Abs_Body_Return_Pct",
    "Overnight_Gap_Pct",
    "Total_Return_Pct",
    "Trailing_ATR20",
    "Body_To_ATR",
    "Body_ATR_Ratio",
    "Trailing_Vol_SMA20",
    "Standard_RVOL",
    "TOD_Vol_SMA20",
    "TOD_RVOL",
    "RVOL",
    "Min_Return_Floor",
    "is_solid",
    "is_high_volume",
    "is_big_magnitude",
    "is_extreme_anomaly",
    "Anomaly_Tier",
    "MTF_Confluence_Count",
    "Datetime_UTC",
    "Datetime_NY",
}

# -----------------------------------------------------------------------------
# Vedic Pillar Feature Categorization
# -----------------------------------------------------------------------------
def categorize_vedic_feature(feature_name: str) -> str:
    """Categorize feature into one of the 10 Classical Vedic Pillars or Astrological Domains."""
    name = feature_name.lower()
    if any(k in name for k in ["declination", "speed", "oob", "station", "julian"]):
        return "Pillar 1: Ephemeris & Speed"
    elif any(k in name for k in ["ang_", "bhv_", "aspect", "combust", "drishti"]):
        return "Pillar 2: Planetary Aspects & Orbs"
    elif any(k in name for k in ["_d9", "_d10", "_d60", "vargottama", "pushkara", "varga"]):
        return "Pillar 3: Harmonic Vargas (D9/D10/D60)"
    elif any(k in name for k in ["jaimini", "_ak", "_amk", "_bk", "_mk", "_pk", "_gk", "_dk"]):
        return "Pillar 4: Jaimini Karakas"
    elif any(k in name for k in ["sav_", "ashtakavarga", "bindu"]):
        return "Pillar 5: Ashtakavarga (SAV)"
    elif any(k in name for k in ["shadbala", "chesta", "kala_bala"]):
        return "Pillar 6: Shadbala Strengths"
    elif any(k in name for k in ["vedha", "sbc", "murti", "sarvatobhadra"]):
        return "Pillar 7: SBC & Vedha Network"
    elif any(k in name for k in ["lagna", "sub_lord", "star_lord", "kp_"]):
        return "Pillar 8: KP Cusps & NYSE Lagna"
    elif any(k in name for k in ["vim_", "dasha", "mahadasha", "antardasha"]):
        return "Pillar 9: Vimshottari Dasha"
    elif any(k in name for k in ["sign", "nakshatra", "pada", "kakshya", "retro"]):
        return "Pillar 10: Zodiacal Signs & Mansions"
    return "Astrological Indicator"


# -----------------------------------------------------------------------------
# Purged & Embargoed Cross-Validation Splitters
# -----------------------------------------------------------------------------
class PurgedTimeSeriesSplit:
    """
    Purged and Embargoed Time Series Cross-Validator for financial time series.
    
    Guarantees strict chronological ordering with:
    - Purging: Removal of training observations immediately preceding test fold to prevent lookahead.
    - Embargo: Optional exclusion window after test fold.
    """

    def __init__(
        self,
        n_splits: int = 5,
        purge_bars: int = 2,
        embargo_pct: float = 0.01,
    ) -> None:
        if n_splits < 2:
            raise ValueError(f"n_splits must be at least 2, got {n_splits}")
        self.n_splits = n_splits
        self.purge_bars = max(0, purge_bars)
        self.embargo_pct = max(0.0, embargo_pct)

    def split(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Optional[Union[pd.Series, np.ndarray]] = None,
        groups: Optional[Union[pd.Series, np.ndarray]] = None,
    ) -> Sequence[Tuple[np.ndarray, np.ndarray]]:
        """Yield (train_indices, test_indices) splits."""
        n_samples = len(X)
        if n_samples < (self.n_splits + 1):
            raise ValueError(
                f"Sample size {n_samples} too small for {self.n_splits} splits."
            )

        test_size = n_samples // (self.n_splits + 1)
        indices = np.arange(n_samples)
        splits: List[Tuple[np.ndarray, np.ndarray]] = []

        for i in range(self.n_splits):
            test_start = (i + 1) * test_size
            test_end = (
                test_start + test_size
                if i < (self.n_splits - 1)
                else n_samples
            )

            train_end = max(0, test_start - self.purge_bars)
            train_idx = indices[:train_end]
            test_idx = indices[test_start:test_end]

            if len(train_idx) > 0 and len(test_idx) > 0:
                splits.append((train_idx, test_idx))

        return splits

    def get_n_splits(
        self,
        X: Optional[Any] = None,
        y: Optional[Any] = None,
        groups: Optional[Any] = None,
    ) -> int:
        return self.n_splits


class PurgedGroupTimeSeriesSplit:
    """
    Purged Group Time Series Splitter ensuring whole groups (e.g. trading days / sessions)
    are kept intact without cross-contamination.
    """

    def __init__(
        self,
        n_splits: int = 5,
        purge_groups: int = 1,
        embargo_pct: float = 0.01,
    ) -> None:
        self.n_splits = n_splits
        self.purge_groups = max(0, purge_groups)
        self.embargo_pct = max(0.0, embargo_pct)

    def split(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Optional[Union[pd.Series, np.ndarray]] = None,
        groups: Optional[Union[pd.Series, np.ndarray]] = None,
    ) -> Sequence[Tuple[np.ndarray, np.ndarray]]:
        if groups is None:
            # Fallback to sample-based PurgedTimeSeriesSplit
            fallback = PurgedTimeSeriesSplit(
                n_splits=self.n_splits,
                purge_bars=self.purge_groups,
                embargo_pct=self.embargo_pct,
            )
            return fallback.split(X, y)

        groups_arr = np.asarray(groups)
        unique_groups = np.unique(groups_arr)
        n_groups = len(unique_groups)

        if n_groups < (self.n_splits + 1):
            fallback = PurgedTimeSeriesSplit(
                n_splits=self.n_splits,
                purge_bars=self.purge_groups,
                embargo_pct=self.embargo_pct,
            )
            return fallback.split(X, y)

        group_test_size = n_groups // (self.n_splits + 1)
        splits: List[Tuple[np.ndarray, np.ndarray]] = []

        for i in range(self.n_splits):
            test_grp_start = (i + 1) * group_test_size
            test_grp_end = (
                test_grp_start + group_test_size
                if i < (self.n_splits - 1)
                else n_groups
            )

            train_grp_end = max(0, test_grp_start - self.purge_groups)
            train_groups_set = set(unique_groups[:train_grp_end])
            test_groups_set = set(unique_groups[test_grp_start:test_grp_end])

            train_idx = np.where(np.isin(groups_arr, list(train_groups_set)))[0]
            test_idx = np.where(np.isin(groups_arr, list(test_groups_set)))[0]

            if len(train_idx) > 0 and len(test_idx) > 0:
                splits.append((train_idx, test_idx))

        return splits


# -----------------------------------------------------------------------------
# Feature Preprocessor
# -----------------------------------------------------------------------------
class VedicFeaturePreprocessor:
    """
    Leak-free feature preprocessor for tabular Vedic astrological and market data.
    
    Categorical strings are encoded via OrdinalEncoder, booleans converted to float,
    and missing values imputed using training set statistics.
    """

    def __init__(
        self,
        exclude_cols: Optional[Sequence[str]] = None,
    ) -> None:
        self.exclude_cols = set(exclude_cols or DEFAULT_TARGET_LEAKAGE_COLS)
        self.cat_cols: List[str] = []
        self.num_cols: List[str] = []
        self.bool_cols: List[str] = []
        self.encoder: Optional[OrdinalEncoder] = None
        self.feature_names_: List[str] = []
        self.num_medians_: Dict[str, float] = {}

    def fit(self, X: pd.DataFrame, y: Optional[Any] = None) -> "VedicFeaturePreprocessor":
        """Fit encoders and compute statistical baselines on training data only."""
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)

        candidate_cols = [c for c in X.columns if c not in self.exclude_cols]

        self.cat_cols = []
        self.num_cols = []
        self.bool_cols = []
        self.num_medians_ = {}

        for col in candidate_cols:
            series = X[col]
            dtype = series.dtype
            if (
                dtype == "object"
                or dtype.name == "category"
                or dtype == "str"
                or dtype == "string"
            ):
                self.cat_cols.append(col)
            elif dtype == "bool" or dtype.name == "boolean":
                self.bool_cols.append(col)
            elif np.issubdtype(dtype, np.number):
                self.num_cols.append(col)
                median_val = float(series.median()) if not pd.isna(series.median()) else 0.0
                self.num_medians_[col] = median_val
            else:
                # Other non-numeric types (e.g. dates) treat as strings
                self.cat_cols.append(col)

        if self.cat_cols:
            self.encoder = OrdinalEncoder(
                handle_unknown="use_encoded_value",
                unknown_value=-1,
            )
            # Fit on string representations
            self.encoder.fit(X[self.cat_cols].astype(str))

        self.feature_names_ = self.num_cols + self.bool_cols + self.cat_cols
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform features into clean numeric float64 DataFrame."""
        if not self.feature_names_:
            raise RuntimeError("Preprocessor has not been fitted.")

        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)

        out_dfs: List[pd.DataFrame] = []

        if self.num_cols:
            num_df = X[self.num_cols].copy()
            for col in self.num_cols:
                median_val = self.num_medians_.get(col, 0.0)
                num_df[col] = pd.to_numeric(num_df[col], errors="coerce").fillna(median_val)
            out_dfs.append(num_df.astype(np.float64))

        if self.bool_cols:
            bool_df = X[self.bool_cols].copy()
            for col in self.bool_cols:
                bool_df[col] = bool_df[col].astype(bool).astype(np.float64)
            out_dfs.append(bool_df.astype(np.float64))

        if self.cat_cols:
            if self.encoder is not None:
                encoded = self.encoder.transform(X[self.cat_cols].astype(str))
                cat_df = pd.DataFrame(
                    encoded,
                    columns=self.cat_cols,
                    index=X.index,
                    dtype=np.float64,
                )
                out_dfs.append(cat_df)

        transformed = pd.concat(out_dfs, axis=1)[self.feature_names_]
        return transformed

    def fit_transform(self, X: pd.DataFrame, y: Optional[Any] = None) -> pd.DataFrame:
        return self.fit(X, y).transform(X)


# -----------------------------------------------------------------------------
# Directional Classification Engine
# -----------------------------------------------------------------------------
def train_directional_models(
    df_anomaly: pd.DataFrame,
    target_col: str = "Candle_Direction",
    cv_splits: int = 5,
    purge_bars: int = 2,
    embargo_pct: float = 0.01,
    models_to_train: Optional[Sequence[str]] = None,
    exclude_cols: Optional[Sequence[str]] = None,
    random_state: int = 42,
) -> Dict[str, Any]:
    """
    Train Directional Classifiers (XGBoost, LightGBM, Random Forest) with Purged Time Series CV.

    Args:
        df_anomaly: DataFrame containing anomaly bars and features.
        target_col: Column name representing direction ('Candle_Direction' or 'Direction').
        cv_splits: Number of cross-validation folds.
        purge_bars: Number of bars to purge before test fold.
        embargo_pct: Fraction for embargo.
        models_to_train: Subset of ['xgboost', 'lightgbm', 'random_forest'].
        exclude_cols: Columns to exclude from training features.
        random_state: Random seed for reproducibility.

    Returns:
        Structured dictionary containing trained models, out-of-sample CV metrics,
        predictions, and best model metadata.
    """
    df = df_anomaly.copy()
    if target_col not in df.columns:
        if "Direction" in df.columns:
            target_col = "Direction"
        else:
            raise KeyError(f"Target column '{target_col}' not found in dataset.")

    # Format target to binary {0, 1}: 1 for GREEN (Bullish), 0 for RED (Bearish)
    y_raw = df[target_col].astype(str).str.upper()
    y_binary = (y_raw == "GREEN") | (y_raw == "BULLISH") | (y_raw == "1")
    y = y_binary.astype(int).values

    # Determine features and preprocess
    excl = set(exclude_cols or DEFAULT_TARGET_LEAKAGE_COLS)
    excl.add(target_col)

    preprocessor = VedicFeaturePreprocessor(exclude_cols=excl)
    preprocessor.fit(df)
    X_full = preprocessor.transform(df)
    feature_names = preprocessor.feature_names_

    # Default models dictionary
    available_models = {
        "xgboost": lambda: xgb.XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=random_state,
            eval_metric="logloss",
            use_label_encoder=False if hasattr(xgb.XGBClassifier, "use_label_encoder") else None,
        ),
        "lightgbm": lambda: lgb.LGBMClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=random_state,
            verbose=-1,
        ),
        "random_forest": lambda: RandomForestClassifier(
            n_estimators=100,
            max_depth=6,
            min_samples_split=5,
            random_state=random_state,
            n_jobs=-1,
        ),
    }

    selected_names = (
        [m for m in models_to_train if m in available_models]
        if models_to_train
        else list(available_models.keys())
    )

    # Purged CV Splitter
    cv_splitter = PurgedTimeSeriesSplit(
        n_splits=cv_splits,
        purge_bars=purge_bars,
        embargo_pct=embargo_pct,
    )
    splits = cv_splitter.split(X_full)

    cv_results: Dict[str, Dict[str, Any]] = {}
    cv_predictions: Dict[str, List[Dict[str, Any]]] = {name: [] for name in selected_names}

    for model_name in selected_names:
        fold_metrics: List[Dict[str, float]] = []

        for fold_idx, (train_idx, test_idx) in enumerate(splits):
            X_train_df = df.iloc[train_idx]
            X_test_df = df.iloc[test_idx]

            # Fit preprocessor on training fold strictly
            fold_prep = VedicFeaturePreprocessor(exclude_cols=excl)
            fold_prep.fit(X_train_df)
            X_tr = fold_prep.transform(X_train_df)
            X_te = fold_prep.transform(X_test_df)

            y_tr, y_te = y[train_idx], y[test_idx]

            model = available_models[model_name]()
            model.fit(X_tr, y_tr)

            # Predict probabilities and classes
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(X_te)[:, 1]
            else:
                probs = model.predict(X_te)

            preds = (probs >= 0.5).astype(int)

            # Calculate metrics
            auc = (
                float(roc_auc_score(y_te, probs))
                if len(np.unique(y_te)) > 1
                else 0.5
            )
            f1 = float(f1_score(y_te, preds, zero_division=0))
            prec = float(precision_score(y_te, preds, zero_division=0))
            rec = float(recall_score(y_te, preds, zero_division=0))
            acc = float(accuracy_score(y_te, preds))
            brier = float(brier_score_loss(y_te, probs))

            fold_metrics.append({
                "fold": fold_idx + 1,
                "auc_roc": auc,
                "f1": f1,
                "precision": prec,
                "recall": rec,
                "accuracy": acc,
                "brier_score": brier,
                "train_size": len(train_idx),
                "test_size": len(test_idx),
            })

            cv_predictions[model_name].append({
                "fold": fold_idx + 1,
                "test_idx": test_idx,
                "y_true": y_te,
                "y_pred": preds,
                "y_prob": probs,
            })

        # Summary across folds
        df_fold_metrics = pd.DataFrame(fold_metrics)
        cv_results[model_name] = {
            "folds": fold_metrics,
            "auc_roc_mean": float(df_fold_metrics["auc_roc"].mean()),
            "auc_roc_std": float(df_fold_metrics["auc_roc"].std()),
            "f1_mean": float(df_fold_metrics["f1"].mean()),
            "f1_std": float(df_fold_metrics["f1"].std()),
            "precision_mean": float(df_fold_metrics["precision"].mean()),
            "recall_mean": float(df_fold_metrics["recall"].mean()),
            "accuracy_mean": float(df_fold_metrics["accuracy"].mean()),
            "brier_score_mean": float(df_fold_metrics["brier_score"].mean()),
        }

    # Fit final models on full dataset
    final_models: Dict[str, Any] = {}
    for model_name in selected_names:
        m = available_models[model_name]()
        m.fit(X_full, y)
        final_models[model_name] = m

    # Select best model based on AUC-ROC
    best_model_name = max(
        selected_names,
        key=lambda k: cv_results[k]["auc_roc_mean"],
    )

    return {
        "models": final_models,
        "cv_metrics": cv_results,
        "cv_predictions": cv_predictions,
        "best_model_name": best_model_name,
        "best_model": final_models[best_model_name],
        "feature_names": feature_names,
        "preprocessor": preprocessor,
        "X_full": X_full,
        "y_true": y,
        "fold_indices": splits,
    }


# -----------------------------------------------------------------------------
# Magnitude Regression Engine
# -----------------------------------------------------------------------------
def train_magnitude_models(
    df_anomaly: pd.DataFrame,
    target_col: str = "Body_To_ATR",
    cv_splits: int = 5,
    purge_bars: int = 2,
    embargo_pct: float = 0.01,
    models_to_train: Optional[Sequence[str]] = None,
    exclude_cols: Optional[Sequence[str]] = None,
    random_state: int = 42,
) -> Dict[str, Any]:
    """
    Train Magnitude Regressors (XGBoost, LightGBM, Random Forest) with Purged Time Series CV.

    Args:
        df_anomaly: DataFrame containing anomaly bars and features.
        target_col: Continuous target feature ('Body_To_ATR' or 'Body_Return_Pct').
        cv_splits: Number of cross-validation folds.
        purge_bars: Number of bars to purge before test fold.
        embargo_pct: Fraction for embargo.
        models_to_train: Subset of ['xgboost', 'lightgbm', 'random_forest'].
        exclude_cols: Columns to exclude from training features.
        random_state: Random seed for reproducibility.

    Returns:
        Structured dictionary containing trained regressors, out-of-sample CV metrics,
        predictions, and best model metadata.
    """
    df = df_anomaly.copy()
    if target_col not in df.columns:
        if "Body_Return_Pct" in df.columns:
            target_col = "Body_Return_Pct"
        else:
            raise KeyError(f"Target column '{target_col}' not found in dataset.")

    y = pd.to_numeric(df[target_col], errors="coerce").fillna(0.0).values

    excl = set(exclude_cols or DEFAULT_TARGET_LEAKAGE_COLS)
    excl.add(target_col)

    preprocessor = VedicFeaturePreprocessor(exclude_cols=excl)
    preprocessor.fit(df)
    X_full = preprocessor.transform(df)
    feature_names = preprocessor.feature_names_

    available_models = {
        "xgboost": lambda: xgb.XGBRegressor(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=random_state,
        ),
        "lightgbm": lambda: lgb.LGBMRegressor(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=random_state,
            verbose=-1,
        ),
        "random_forest": lambda: RandomForestRegressor(
            n_estimators=100,
            max_depth=6,
            min_samples_split=5,
            random_state=random_state,
            n_jobs=-1,
        ),
    }

    selected_names = (
        [m for m in models_to_train if m in available_models]
        if models_to_train
        else list(available_models.keys())
    )

    cv_splitter = PurgedTimeSeriesSplit(
        n_splits=cv_splits,
        purge_bars=purge_bars,
        embargo_pct=embargo_pct,
    )
    splits = cv_splitter.split(X_full)

    cv_results: Dict[str, Dict[str, Any]] = {}
    cv_predictions: Dict[str, List[Dict[str, Any]]] = {name: [] for name in selected_names}

    for model_name in selected_names:
        fold_metrics: List[Dict[str, float]] = []

        for fold_idx, (train_idx, test_idx) in enumerate(splits):
            X_train_df = df.iloc[train_idx]
            X_test_df = df.iloc[test_idx]

            fold_prep = VedicFeaturePreprocessor(exclude_cols=excl)
            fold_prep.fit(X_train_df)
            X_tr = fold_prep.transform(X_train_df)
            X_te = fold_prep.transform(X_test_df)

            y_tr, y_te = y[train_idx], y[test_idx]

            model = available_models[model_name]()
            model.fit(X_tr, y_tr)
            preds = model.predict(X_te)

            rmse = float(root_mean_squared_error(y_te, preds))
            mae = float(mean_absolute_error(y_te, preds))
            r2 = float(r2_score(y_te, preds))

            if np.std(preds) > 1e-8 and np.std(y_te) > 1e-8:
                rho, _ = spearmanr(y_te, preds)
                pear, _ = pearsonr(y_te, preds)
                spearman_val = float(rho) if not np.isnan(rho) else 0.0
                pearson_val = float(pear) if not np.isnan(pear) else 0.0
            else:
                spearman_val, pearson_val = 0.0, 0.0

            fold_metrics.append({
                "fold": fold_idx + 1,
                "rmse": rmse,
                "mae": mae,
                "r2": r2,
                "spearman_corr": spearman_val,
                "pearson_corr": pearson_val,
                "train_size": len(train_idx),
                "test_size": len(test_idx),
            })

            cv_predictions[model_name].append({
                "fold": fold_idx + 1,
                "test_idx": test_idx,
                "y_true": y_te,
                "y_pred": preds,
            })

        df_fold_metrics = pd.DataFrame(fold_metrics)
        cv_results[model_name] = {
            "folds": fold_metrics,
            "rmse_mean": float(df_fold_metrics["rmse"].mean()),
            "rmse_std": float(df_fold_metrics["rmse"].std()),
            "mae_mean": float(df_fold_metrics["mae"].mean()),
            "r2_mean": float(df_fold_metrics["r2"].mean()),
            "spearman_corr_mean": float(df_fold_metrics["spearman_corr"].mean()),
            "pearson_corr_mean": float(df_fold_metrics["pearson_corr"].mean()),
        }

    final_models: Dict[str, Any] = {}
    for model_name in selected_names:
        m = available_models[model_name]()
        m.fit(X_full, y)
        final_models[model_name] = m

    best_model_name = min(
        selected_names,
        key=lambda k: cv_results[k]["rmse_mean"],
    )

    return {
        "models": final_models,
        "cv_metrics": cv_results,
        "cv_predictions": cv_predictions,
        "best_model_name": best_model_name,
        "best_model": final_models[best_model_name],
        "feature_names": feature_names,
        "preprocessor": preprocessor,
        "X_full": X_full,
        "y_true": y,
        "fold_indices": splits,
    }


# -----------------------------------------------------------------------------
# TreeSHAP Global Feature Attribution
# -----------------------------------------------------------------------------
def compute_shap_feature_attributions(
    model: Any,
    X_train: Union[pd.DataFrame, np.ndarray],
    X_test: Optional[Union[pd.DataFrame, np.ndarray]] = None,
    feature_names: Optional[Sequence[str]] = None,
    top_n: int = 20,
) -> Dict[str, Any]:
    """
    Compute exact TreeSHAP feature attributions across all features.

    Args:
        model: Trained tree-based model (XGBoost, LightGBM, Random Forest).
        X_train: Training data or full dataset matrix.
        X_test: Optional test evaluation matrix (if None, X_train is evaluated).
        feature_names: Feature column names.
        top_n: Number of top features to extract (default 20).

    Returns:
        Dictionary containing shap_values, mean_abs_shap series, top_20_features df,
        summary_df, and explainer instance.
    """
    if isinstance(X_train, pd.DataFrame):
        if feature_names is None:
            feature_names = list(X_train.columns)
        X_eval = X_test if X_test is not None else X_train
        X_eval_mat = X_eval.values if isinstance(X_eval, pd.DataFrame) else X_eval
    else:
        X_eval_mat = X_test if X_test is not None else X_train
        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(X_eval_mat.shape[1])]

    explainer = shap.TreeExplainer(model)
    shap_vals_raw = explainer.shap_values(X_eval_mat)

    # Standardize shap_values tensor shape to (N_samples, N_features)
    if isinstance(shap_vals_raw, list):
        # Binary classification list: pick class 1 (Bullish/Green)
        shap_vals = np.array(shap_vals_raw[1]) if len(shap_vals_raw) > 1 else np.array(shap_vals_raw[0])
    elif isinstance(shap_vals_raw, np.ndarray):
        if shap_vals_raw.ndim == 3:
            # Shape (N, F, 2) from RandomForest
            shap_vals = shap_vals_raw[:, :, 1] if shap_vals_raw.shape[2] > 1 else shap_vals_raw[:, :, 0]
        else:
            shap_vals = shap_vals_raw
    else:
        shap_vals = np.asarray(shap_vals_raw)

    # Compute mean absolute SHAP value \overline{|\phi_j|}
    mean_abs_shap = np.mean(np.abs(shap_vals), axis=0)
    std_shap = np.std(shap_vals, axis=0)

    # Compute directional impact correlation
    directional_corrs = []
    for j in range(len(feature_names)):
        feat_col = X_eval_mat[:, j]
        shap_col = shap_vals[:, j]
        if np.std(feat_col) > 1e-8 and np.std(shap_col) > 1e-8:
            r, _ = pearsonr(feat_col, shap_col)
            directional_corrs.append(float(r) if not np.isnan(r) else 0.0)
        else:
            directional_corrs.append(0.0)

    # Construct complete summary DataFrame
    summary_records = []
    for rank_idx, feat_idx in enumerate(np.argsort(-mean_abs_shap)):
        fname = feature_names[feat_idx]
        m_val = float(mean_abs_shap[feat_idx])
        s_val = float(std_shap[feat_idx])
        d_corr = directional_corrs[feat_idx]
        pillar = categorize_vedic_feature(fname)

        summary_records.append({
            "rank": rank_idx + 1,
            "feature": fname,
            "mean_abs_shap": m_val,
            "std_shap": s_val,
            "directional_corr": d_corr,
            "pillar": pillar,
            "feature_index": feat_idx,
        })

    summary_df = pd.DataFrame(summary_records)
    top_n_df = summary_df.head(top_n).copy()

    mean_abs_series = pd.Series(
        mean_abs_shap,
        index=feature_names,
        name="mean_abs_shap",
    ).sort_values(ascending=False)

    return {
        "shap_values": shap_vals,
        "mean_abs_shap": mean_abs_series,
        "top_20_features": top_n_df,
        "summary_df": summary_df,
        "explainer": explainer,
        "feature_names": list(feature_names),
    }


# -----------------------------------------------------------------------------
# SHAP Pairwise Interaction Values Mining
# -----------------------------------------------------------------------------
def compute_shap_interactions(
    model: Any,
    X_sample: Union[pd.DataFrame, np.ndarray],
    feature_names: Optional[Sequence[str]] = None,
    top_n: int = 20,
    max_sample_size: int = 100,
    random_state: int = 42,
) -> Dict[str, Any]:
    """
    Compute second-order SHAP interaction tensors and extract top pairwise synergies.

    Args:
        model: Trained tree-based model.
        X_sample: Sample feature matrix.
        feature_names: Feature column names.
        top_n: Number of top pairwise interactions to extract.
        max_sample_size: Cap on sample size for fast interaction calculation.
        random_state: Random seed for sample selection.

    Returns:
        Dictionary with interaction_matrix, top_pairwise_interactions df,
        and top_features_matrix for heatmap plotting.
    """
    if isinstance(X_sample, pd.DataFrame):
        if feature_names is None:
            feature_names = list(X_sample.columns)
        if len(X_sample) > max_sample_size:
            rng = np.random.RandomState(random_state)
            sample_idx = rng.choice(len(X_sample), size=max_sample_size, replace=False)
            X_eval_mat = X_sample.iloc[sample_idx].values
        else:
            X_eval_mat = X_sample.values
    else:
        X_eval_mat = X_sample
        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(X_eval_mat.shape[1])]
        if len(X_eval_mat) > max_sample_size:
            rng = np.random.RandomState(random_state)
            sample_idx = rng.choice(len(X_eval_mat), size=max_sample_size, replace=False)
            X_eval_mat = X_eval_mat[sample_idx]

    explainer = shap.TreeExplainer(model)
    raw_interactions = explainer.shap_interaction_values(X_eval_mat)

    # Standardize interaction shape to (N_samples, N_features, N_features)
    if isinstance(raw_interactions, list):
        iv = np.array(raw_interactions[1]) if len(raw_interactions) > 1 else np.array(raw_interactions[0])
    elif isinstance(raw_interactions, np.ndarray):
        if raw_interactions.ndim == 4:
            # (N, F, F, 2)
            iv = raw_interactions[:, :, :, 1] if raw_interactions.shape[3] > 1 else raw_interactions[:, :, :, 0]
        else:
            iv = raw_interactions
    else:
        iv = np.asarray(raw_interactions)

    # Compute mean absolute interaction matrix: shape (N_features, N_features)
    mean_abs_interaction = np.mean(np.abs(iv), axis=0)

    n_feats = len(feature_names)
    interaction_df = pd.DataFrame(
        mean_abs_interaction,
        index=feature_names,
        columns=feature_names,
    )

    # Extract upper triangular non-diagonal pairs
    pair_records: List[Dict[str, Any]] = []
    for i in range(n_feats):
        for j in range(i + 1, n_feats):
            score = float(mean_abs_interaction[i, j])
            f1, f2 = feature_names[i], feature_names[j]
            p1 = categorize_vedic_feature(f1)
            p2 = categorize_vedic_feature(f2)
            desc = f"{f1} ({p1.split(':')[0]}) × {f2} ({p2.split(':')[0]})"

            pair_records.append({
                "feature_1": f1,
                "feature_2": f2,
                "interaction_score": score,
                "pillar_1": p1,
                "pillar_2": p2,
                "description": desc,
                "idx_1": i,
                "idx_2": j,
            })

    top_pairs_df = (
        pd.DataFrame(pair_records)
        .sort_values("interaction_score", ascending=False)
        .reset_index(drop=True)
    )
    top_pairs_df["rank"] = top_pairs_df.index + 1
    top_pairs_n = top_pairs_df.head(top_n).copy()

    # Identify the top interacting unique features to form a dense submatrix
    top_feat_set = set()
    for _, row in top_pairs_n.iterrows():
        top_feat_set.add(row["feature_1"])
        top_feat_set.add(row["feature_2"])

    top_feat_list = [f for f in feature_names if f in top_feat_set][:top_n]
    if len(top_feat_list) < 5:
        # Fallback to top diagonal features
        diag_scores = np.diag(mean_abs_interaction)
        top_indices = np.argsort(-diag_scores)[:top_n]
        top_feat_list = [feature_names[idx] for idx in top_indices]

    top_submatrix = interaction_df.loc[top_feat_list, top_feat_list]

    return {
        "interaction_values": iv,
        "interaction_matrix": interaction_df,
        "top_pairwise_interactions": top_pairs_n,
        "all_pairwise_interactions": top_pairs_df,
        "top_features_matrix": top_submatrix,
        "top_features_list": top_feat_list,
    }


# -----------------------------------------------------------------------------
# Visualization Export Helpers
# -----------------------------------------------------------------------------
def plot_top_features_shap(
    shap_dict: Dict[str, Any],
    output_path: str = "reports/charts/shap_top20_global.png",
    top_n: int = 20,
    title: Optional[str] = None,
) -> str:
    """
    Plot and save a high-resolution horizontal bar chart of Top 20 Global Driver Features.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    top_df = shap_dict["top_20_features"].head(top_n).copy()

    # Sort ascending for horizontal bar chart (top ranked at top)
    plot_df = top_df.sort_values("mean_abs_shap", ascending=True).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FAFAFA")

    # Color gradient based on mean_abs_shap
    norm = plt.Normalize(plot_df["mean_abs_shap"].min(), plot_df["mean_abs_shap"].max())
    colors = plt.cm.viridis(norm(plot_df["mean_abs_shap"].values))

    bars = ax.barh(
        plot_df["feature"],
        plot_df["mean_abs_shap"],
        color=colors,
        edgecolor="#2C3E50",
        linewidth=0.8,
        height=0.65,
    )

    # Annotate bar values
    max_val = plot_df["mean_abs_shap"].max()
    for bar, val in zip(bars, plot_df["mean_abs_shap"]):
        ax.text(
            val + (max_val * 0.015),
            bar.get_y() + bar.get_height() / 2.0,
            f"{val:.4f}",
            va="center",
            ha="left",
            fontsize=9,
            fontweight="bold",
            color="#2C3E50",
        )

    chart_title = title or "Top 20 Omni-Vedic Global Driver Features (TreeSHAP)"
    ax.set_title(chart_title, fontsize=15, fontweight="bold", pad=15, color="#1A252F")
    ax.set_xlabel("Mean Absolute SHAP Value  E[|phi_j|]", fontsize=12, fontweight="bold", labelpad=10)
    ax.set_ylabel("Vedic Astrological / Celestial Feature", fontsize=12, fontweight="bold", labelpad=10)

    ax.grid(axis="x", linestyle="--", alpha=0.5, color="#BDC3C7")
    ax.set_axisbelow(True)
    ax.set_xlim(0, max_val * 1.15)
    plt.tight_layout()

    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


def plot_interaction_heatmap(
    interaction_dict: Dict[str, Any],
    output_path: str = "reports/charts/shap_interaction_heatmap.png",
    top_n: int = 15,
    title: Optional[str] = None,
) -> str:
    """
    Plot and save a high-resolution heatmap of SHAP pairwise feature interactions.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    submatrix = interaction_dict["top_features_matrix"].iloc[:top_n, :top_n]

    fig, ax = plt.subplots(figsize=(12, 10), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")

    sns.heatmap(
        submatrix,
        annot=True,
        fmt=".3f",
        cmap="YlGnBu",
        cbar_kws={"label": "Mean Absolute Interaction Strength  E[|Phi_{j,k}|]"},
        linewidths=0.5,
        linecolor="#E2E8F0",
        ax=ax,
        annot_kws={"size": 8, "weight": "bold"},
    )

    chart_title = title or "Pairwise SHAP Interaction Matrix (Second-Order Synergies)"
    ax.set_title(chart_title, fontsize=15, fontweight="bold", pad=15, color="#1A252F")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", fontsize=9, fontweight="semibold")
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=9, fontweight="semibold")

    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


def generate_all_ml_charts(
    shap_results: Dict[str, Any],
    interaction_results: Dict[str, Any],
    output_dir: str = "reports/charts",
) -> List[str]:
    """
    Generate all required high-resolution visual charts into the reports/charts directory.
    """
    os.makedirs(output_dir, exist_ok=True)
    saved_files: List[str] = []

    # 1. Top 20 Global Driver Features SHAP Bar Chart
    top20_path = os.path.join(output_dir, "shap_top20_global.png")
    plot_top_features_shap(shap_results, output_path=top20_path, top_n=20)
    saved_files.append(top20_path)

    # 2. Pairwise SHAP Interaction Heatmap
    heatmap_path = os.path.join(output_dir, "shap_interaction_heatmap.png")
    plot_interaction_heatmap(interaction_results, output_path=heatmap_path, top_n=15)
    saved_files.append(heatmap_path)

    return saved_files


# -----------------------------------------------------------------------------
# End-to-End Master Discovery Engine Runner
# -----------------------------------------------------------------------------
def run_vedic_ml_discovery_engine(
    df_anomaly: Optional[pd.DataFrame] = None,
    parquet_path: str = "data/spy_anomalies_omni_vedic_supreme.parquet",
    output_dir: str = "reports/charts",
    cv_splits: int = 5,
    generate_charts: bool = True,
    sample_for_interactions: int = 100,
    random_state: int = 42,
) -> Dict[str, Any]:
    """
    Master coordinator executing full ML attribution & interaction discovery pipeline.
    """
    if df_anomaly is None:
        if not os.path.exists(parquet_path):
            raise FileNotFoundError(f"Parquet dataset not found at: {parquet_path}")
        df_anomaly = pd.read_parquet(parquet_path)

    # 1. Train Directional Classifiers
    directional_res = train_directional_models(
        df_anomaly=df_anomaly,
        target_col="Candle_Direction",
        cv_splits=cv_splits,
        random_state=random_state,
    )

    # 2. Train Magnitude Regressors
    magnitude_res = train_magnitude_models(
        df_anomaly=df_anomaly,
        target_col="Body_To_ATR",
        cv_splits=cv_splits,
        random_state=random_state,
    )

    # 3. Compute TreeSHAP Global Attributions on Best Directional Model
    best_clf = directional_res["best_model"]
    X_full = directional_res["X_full"]
    feature_names = directional_res["feature_names"]

    shap_res = compute_shap_feature_attributions(
        model=best_clf,
        X_train=X_full,
        feature_names=feature_names,
        top_n=20,
    )

    # 4. Compute Pairwise SHAP Interactions
    interaction_res = compute_shap_interactions(
        model=best_clf,
        X_sample=X_full,
        feature_names=feature_names,
        top_n=20,
        max_sample_size=sample_for_interactions,
        random_state=random_state,
    )

    # 5. Generate & Save High-Resolution Visual Charts
    saved_charts = []
    if generate_charts:
        saved_charts = generate_all_ml_charts(
            shap_results=shap_res,
            interaction_results=interaction_res,
            output_dir=output_dir,
        )

    return {
        "directional_results": directional_res,
        "magnitude_results": magnitude_res,
        "shap_results": shap_res,
        "interaction_results": interaction_res,
        "top_20_features": shap_res["top_20_features"],
        "top_pairwise_interactions": interaction_res["top_pairwise_interactions"],
        "saved_charts": saved_charts,
    }


if __name__ == "__main__":
    print("Executing Vedic Quant Machine Learning Discovery Engine...")
    results = run_vedic_ml_discovery_engine()
    print("\n--- Out-of-Sample Directional Classification Metrics ---")
    for mname, mmetrics in results["directional_results"]["cv_metrics"].items():
        print(
            f"  {mname:15s} | AUC: {mmetrics['auc_roc_mean']:.4f} +/- {mmetrics['auc_roc_std']:.4f} "
            f"| F1: {mmetrics['f1_mean']:.4f} | Acc: {mmetrics['accuracy_mean']:.4f} | Brier: {mmetrics['brier_score_mean']:.4f}"
        )

    print("\n--- Out-of-Sample Magnitude Regression Metrics ---")
    for mname, mmetrics in results["magnitude_results"]["cv_metrics"].items():
        print(
            f"  {mname:15s} | RMSE: {mmetrics['rmse_mean']:.4f} +/- {mmetrics['rmse_std']:.4f} "
            f"| MAE: {mmetrics['mae_mean']:.4f} | Spearman: {mmetrics['spearman_corr_mean']:.4f}"
        )

    print("\n--- Top 10 Global Driver Features (TreeSHAP) ---")
    print(results["top_20_features"][["rank", "feature", "mean_abs_shap", "pillar"]].head(10).to_string(index=False))

    print("\n--- Top 10 Pairwise Feature Interactions (TreeSHAP) ---")
    print(
        results["top_pairwise_interactions"][["rank", "feature_1", "feature_2", "interaction_score"]].head(10).to_string(index=False)
    )

    print(f"\nSaved Charts: {results['saved_charts']}")
