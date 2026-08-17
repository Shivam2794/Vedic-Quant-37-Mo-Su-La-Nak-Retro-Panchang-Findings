"""
VEDIC PATTERN MINER & STATISTICAL SIGNIFICANCE SIEVE ENGINE
===========================================================
High-throughput, mathematically rigorous discovery and significance testing
engine for Omni-Vedic astrological market anomaly correlations.

Core Capabilities:
  1. R1: Baseline Null Calibration Engine (Generates/loads 33k+ RTH continuous baseline).
  2. R2: Univariate Statistical Significance & Empirical Lift Ratio Engine:
         - Fisher's Exact Test (2x2 contingency)
         - Chi-Square Contingency Test
         - Benjamini-Hochberg False Discovery Rate (FDR) correction (q < 0.05 / p < 0.01)
         - Two-sample Kolmogorov-Smirnov (KS) & Mann-Whitney U continuous tests with Cohen's d.
  3. R3: Higher-Order Combinatorial Pattern Mining (Multi-Planet Confluences):
         - FP-Growth (mlxtend) and explicit k-way (2, 3, 4-way) conjunction miner.
         - Strict thresholds: Support >= 10, Confidence >= 70%, Lift >= 2.0x, p < 0.005.
         - Shallow Decision Tree rule extraction (interpretable decision boundaries).
         - Non-parametric permutation test (N=1000) for empirical p-values.
  4. R5: Deep Vedic 10-Pillar Forensic Drilldown:
         - Pillar 1: Ephemeris & Declinations (OOB |delta| > 23.44, Stations).
         - Pillar 2: Mutual Aspects & Bhavas (6/8 Shadashtaka, 2/12 Dwirdwadasa, 1/7 Samasaptaka).
         - Pillar 3: Divisional Vargas (D1..D60, Vargottama, Pushkara Navamsha).
         - Pillar 4: Jaimini Chara Karakas (GK Crash Karaka vs AK Soul/Trend Karaka).
         - Pillar 5: Ashtakavarga & SAV Point Thresholds (< 25 Crisis vs > 32 Support).
         - Pillar 6: Shadbala 6-Fold Potency & Classical Combustion.
         - Pillar 7: Sarvatobhadra Chakra & Vedha Network (Malefic Nakshatras & Kakshyas).
         - Pillar 8: KP Sub-Lords & Star-Lords (NYSE Lagna & Planetary Cusps).
         - Pillar 9: NYSE Natal Vimshottari Dashas (MD/AD/PD cycles from 1792).
         - Pillar 10: Multi-Timeframe Confluence & Resonance Profiles.
"""

import os
import sys
import math
import time
import logging
from typing import Dict, List, Tuple, Set, Optional, Union, Any
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
import scipy.stats as stats
from statsmodels.stats.multitest import multipletests
from sklearn.tree import DecisionTreeClassifier, export_text
from mlxtend.frequent_patterns import fpgrowth, association_rules
import swisseph as swe

# ═══════════════════════════════════════════════════════════════
# PATH SETUP & IMPORT OF VEDIC ASTROLOGY FUSION ENGINES
# ═══════════════════════════════════════════════════════════════
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, ".."))
_ROOT_DIR = os.path.abspath(os.path.join(_SRC_DIR, ".."))

if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)
if os.path.join(_SRC_DIR, "vedic_astrology") not in sys.path:
    sys.path.insert(0, os.path.join(_SRC_DIR, "vedic_astrology"))
if os.path.join(_SRC_DIR, "core") not in sys.path:
    sys.path.insert(0, os.path.join(_SRC_DIR, "core"))

from omni_vedic_fusion import (
    extract_omni_vedic_row,
    SIGNS,
    NAKSHATRAS,
    KAKSHYA_LORDS,
    GRAHA_MAP,
    COMBUSTION_ORBS,
)

logger = logging.getLogger(__name__)

# Out of bounds ecliptic declination threshold (degrees)
OOB_DECLINATION_THRESHOLD = 23.44

# Planetary speed stationary threshold (degrees/day)
STATIONARY_SPEED_THRESHOLD = 0.05


# ═══════════════════════════════════════════════════════════════
# MULTIPROCESSING WORKER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def _worker_extract_omni_batch(jd_batch: List[float]) -> List[Dict[str, Any]]:
    """Worker function for batch extraction of Omni-Vedic features."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    results = []
    for jd in jd_batch:
        try:
            row = extract_omni_vedic_row(jd)
            results.append(row)
        except Exception as e:
            results.append({"_error": str(e)})
    return results


# ═══════════════════════════════════════════════════════════════
# R1: BASELINE NULL CALIBRATION ENGINE
# ═══════════════════════════════════════════════════════════════

def generate_rth_baseline_dataset(
    input_parquet: Optional[str] = None,
    output_parquet: Optional[str] = None,
    sample_limit: Optional[int] = None,
    force_recompute: bool = False,
    max_workers: Optional[int] = None,
    batch_size: int = 500,
) -> pd.DataFrame:
    """
    Loads historical SPY 1H unified data (2008-2026), filters strictly for
    Regular Trading Hours (09:30 to 16:00 EST), and enriches with all 397 Omni-Vedic
    astrological features via parallel Swiss Ephemeris extraction.

    Args:
        input_parquet: Path to raw SPY 1H parquet.
        output_parquet: Path to save/load cached baseline dataset.
        sample_limit: Optional integer limit for testing/benchmarks.
        force_recompute: If True, re-enriches even if cached file exists.
        max_workers: Number of parallel CPU workers.
        batch_size: Batch size per worker process.

    Returns:
        pd.DataFrame containing fully enriched baseline dataset.
    """
    if input_parquet is None:
        input_parquet = os.path.join(_ROOT_DIR, "data", "raw_spy_1h_unified_2008_2026.parquet")
    if output_parquet is None:
        output_parquet = os.path.join(_ROOT_DIR, "data", "spy_continuous_rth_omni_vedic_baseline.parquet")

    # 1. Check cache
    if not force_recompute and os.path.exists(output_parquet) and sample_limit is None:
        logger.info(f"Loading cached baseline dataset from: {output_parquet}")
        df_cached = pd.read_parquet(output_parquet)
        logger.info(f"Loaded cached baseline shape: {df_cached.shape}")
        return df_cached

    if not os.path.exists(input_parquet):
        raise FileNotFoundError(f"Raw SPY 1H unified dataset not found at: {input_parquet}")

    logger.info(f"Reading raw SPY 1H data from: {input_parquet}")
    df_raw = pd.read_parquet(input_parquet)

    # 2. Filter strictly for RTH session (09:30 - 16:00 EST)
    dt_ny = pd.to_datetime(df_raw["Datetime_NY"])
    # 09:30 to 15:30 bar start times (or 09:30 <= time <= 16:00)
    is_rth = (
        (dt_ny.dt.hour >= 9)
        & (dt_ny.dt.hour <= 15)
        & ~((dt_ny.dt.hour == 9) & (dt_ny.dt.minute < 30))
    )
    df_rth = df_raw[is_rth].copy().reset_index(drop=True)
    logger.info(f"Filtered {len(df_raw)} total bars down to {len(df_rth)} continuous RTH bars.")

    if sample_limit is not None and sample_limit > 0:
        df_rth = df_rth.iloc[:sample_limit].copy().reset_index(drop=True)
        logger.info(f"Applied sample limit: {len(df_rth)} bars.")

    # 3. Calculate Julian Date UT if missing
    if "Julian_Date_UT" not in df_rth.columns or df_rth["Julian_Date_UT"].isna().any():
        logger.info("Computing Julian Date UT for baseline bars...")
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        dt_utc = pd.to_datetime(df_rth["Datetime_UTC"])
        jds = []
        for dt in dt_utc:
            hour_frac = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
            jds.append(swe.julday(dt.year, dt.month, dt.day, hour_frac))
        df_rth["Julian_Date_UT"] = jds

    jd_list = df_rth["Julian_Date_UT"].tolist()
    total_bars = len(jd_list)
    logger.info(f"Starting parallel Vedic enrichment for {total_bars} baseline bars...")

    # 4. Batch extraction using ProcessPoolExecutor
    batches = [jd_list[i : i + batch_size] for i in range(0, total_bars, batch_size)]
    if max_workers is None:
        max_workers = min(os.cpu_count() or 4, 16)

    t0 = time.time()
    extracted_rows = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        batch_results = list(executor.map(_worker_extract_omni_batch, batches))
        for res in batch_results:
            extracted_rows.extend(res)

    t1 = time.time()
    logger.info(f"Enrichment complete in {t1 - t0:.2f}s ({total_bars / max(t1 - t0, 0.001):.1f} bars/sec).")

    # 5. Merge baseline price/volume columns with extracted Vedic features
    df_vedic = pd.DataFrame(extracted_rows)
    # Remove any potential internal error keys
    if "_error" in df_vedic.columns:
        df_vedic = df_vedic.drop(columns=["_error"])

    # Combine dataframes
    df_baseline = pd.concat([df_rth, df_vedic], axis=1)

    # 6. Add standard baseline indicator columns if not present
    if "Candle_Direction" not in df_baseline.columns:
        df_baseline["Candle_Direction"] = np.where(
            df_baseline["Close"] >= df_baseline["Open"], "GREEN", "RED"
        )
    if "Direction" not in df_baseline.columns:
        df_baseline["Direction"] = df_baseline["Candle_Direction"]
    if "Timeframe" not in df_baseline.columns:
        df_baseline["Timeframe"] = "1H"

    # Validation: Check zero NaNs in core position columns
    core_cols = [c for c in df_baseline.columns if c.endswith("_Lon") or c.endswith("_Speed")]
    nan_count = df_baseline[core_cols].isna().sum().sum()
    if nan_count > 0:
        logger.warning(f"Warning: {nan_count} NaNs found in baseline planetary position columns!")
    else:
        logger.info("Zero-NaN validation on baseline planetary features: PASSED.")

    # 7. Save to cache
    if sample_limit is None:
        os.makedirs(os.path.dirname(output_parquet), exist_ok=True)
        df_baseline.to_parquet(output_parquet, index=False)
        logger.info(f"Saved complete baseline dataset to: {output_parquet} (Shape: {df_baseline.shape})")

    return df_baseline


# ═══════════════════════════════════════════════════════════════
# FEATURE DISCRETIZATION & NORMALIZATION HELPER
# ═══════════════════════════════════════════════════════════════

def get_discrete_feature_columns(df: pd.DataFrame) -> List[str]:
    """Identifies all categorical, discrete ordinal, and binary columns in dataset."""
    discrete_cols = []
    for col in df.columns:
        if col in [
            "Datetime_UTC", "Datetime_NY", "Julian_Date_UT", "Open", "High", "Low", "Close",
            "Volume", "Real_Body", "Body", "Candle_Range", "Range", "Trailing_ATR20",
            "Body_To_ATR", "Body_ATR_Ratio", "Trailing_Vol_SMA20", "Standard_RVOL",
            "TOD_Vol_SMA20", "TOD_RVOL", "RVOL", "Min_Return_Floor", "Body_Return_Pct",
            "Abs_Body_Return_Pct", "Overnight_Gap_Pct", "Total_Return_Pct", "Upper_Wick",
            "Lower_Wick", "Upper_Wick_Ratio", "Lower_Wick_Ratio", "Solid_Ratio", "Max_Wick_Ratio"
        ]:
            continue

        if pd.api.types.is_string_dtype(df[col]) or pd.api.types.is_object_dtype(df[col]) or isinstance(df[col].dtype, pd.CategoricalDtype):
            discrete_cols.append(col)
        elif any(col.endswith(sfx) for sfx in ["_Retro", "_Combust", "_Vargottama", "_Pada", "_D9", "_D10", "_D60"]):
            discrete_cols.append(col)
        elif col.startswith("Bhv_") or col.startswith("is_"):
            discrete_cols.append(col)
        elif col in ["Hour_Of_Day", "Anomaly_Tier", "MTF_Confluence_Count"]:
            discrete_cols.append(col)

    return list(dict.fromkeys(discrete_cols))


def get_continuous_feature_columns(df: pd.DataFrame) -> List[str]:
    """Identifies all continuous numeric astronomical features."""
    continuous_cols = []
    for col in df.columns:
        if col in [
            "Datetime_UTC", "Datetime_NY", "Julian_Date_UT", "Open", "High", "Low", "Close",
            "Volume", "Real_Body", "Body", "Candle_Range", "Range", "Trailing_ATR20",
            "Body_To_ATR", "Body_ATR_Ratio", "Trailing_Vol_SMA20", "Standard_RVOL",
            "TOD_Vol_SMA20", "TOD_RVOL", "RVOL", "Min_Return_Floor", "Body_Return_Pct",
            "Abs_Body_Return_Pct", "Overnight_Gap_Pct", "Total_Return_Pct", "Upper_Wick",
            "Lower_Wick", "Upper_Wick_Ratio", "Lower_Wick_Ratio", "Solid_Ratio", "Max_Wick_Ratio"
        ]:
            continue

        if pd.api.types.is_numeric_dtype(df[col]):
            if any(col.endswith(sfx) for sfx in ["_Speed", "_Declination", "_Lon", "_DegInSign", "_Rupas", "_Ratio"]):
                continuous_cols.append(col)
            elif col.startswith("Ang_") or col.startswith("SAV_") or (col.startswith("Jaimini_") and col.endswith("_Deg")):
                continuous_cols.append(col)
            elif col in ["Ayanamsha_Val"]:
                continuous_cols.append(col)

    return list(dict.fromkeys(continuous_cols))


# ═══════════════════════════════════════════════════════════════
# R2: UNIVARIATE STATISTICAL SIGNIFICANCE & LIFT ENGINE
# ═══════════════════════════════════════════════════════════════

def compute_univariate_lift(
    df_anomaly: pd.DataFrame,
    df_baseline: pd.DataFrame,
    target_class: str = "ALL",
    min_support: int = 5,
    discrete_cols: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Computes Empirical Lift for every discrete Vedic state:
      Lift = P(Feature=v | Anomaly) / P(Feature=v | Baseline)

    Args:
        df_anomaly: Anomaly dataset (e.g. 1,408 rows).
        df_baseline: Continuous baseline dataset (e.g. 33k+ bars).
        target_class: 'ALL', 'GREEN', 'RED', etc.
        min_support: Minimum anomaly count threshold.
        discrete_cols: Optional list of discrete columns to test.

    Returns:
        pd.DataFrame sorted by Lift descending.
    """
    # Filter anomaly target subset if requested
    df_a = df_anomaly.copy()
    if target_class.upper() != "ALL":
        dir_col = "Candle_Direction" if "Candle_Direction" in df_a.columns else "Direction"
        if dir_col in df_a.columns:
            df_a = df_a[df_a[dir_col].astype(str).str.upper() == target_class.upper()].copy()

    n_a = len(df_a)
    n_b = len(df_baseline)
    if n_a == 0 or n_b == 0:
        return pd.DataFrame(
            columns=[
                "Feature", "Value", "Target_Class", "Anomaly_Count", "Anomaly_Total",
                "Anomaly_Prob", "Baseline_Count", "Baseline_Total", "Baseline_Prob", "Lift"
            ]
        )

    if discrete_cols is None:
        discrete_cols = get_discrete_feature_columns(df_a)

    records = []
    for col in discrete_cols:
        if col not in df_baseline.columns:
            continue

        # Get counts in anomaly and baseline
        counts_a = df_a[col].value_counts()
        counts_b = df_baseline[col].value_counts()

        for val, k_a in counts_a.items():
            if k_a < min_support:
                continue

            k_b = counts_b.get(val, 0)
            p_a = k_a / n_a
            p_b = k_b / n_b if n_b > 0 else 0.0

            lift = (p_a / p_b) if p_b > 0 else (np.inf if p_a > 0 else 0.0)

            records.append({
                "Feature": col,
                "Value": str(val),
                "Target_Class": target_class.upper(),
                "Anomaly_Count": int(k_a),
                "Anomaly_Total": int(n_a),
                "Anomaly_Prob": round(float(p_a), 6),
                "Baseline_Count": int(k_b),
                "Baseline_Total": int(n_b),
                "Baseline_Prob": round(float(p_b), 6),
                "Lift": round(float(lift), 4),
            })

    df_lift = pd.DataFrame(records)
    if not df_lift.empty:
        df_lift = df_lift.sort_values(by=["Lift", "Anomaly_Count"], ascending=[False, False]).reset_index(drop=True)

    return df_lift


def run_fdr_significance_sieve(
    df_anomaly: pd.DataFrame,
    df_baseline: pd.DataFrame,
    alpha: float = 0.01,
    fdr_threshold: float = 0.05,
    target_class: str = "ALL",
    min_support: int = 5,
    discrete_cols: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Executes 2x2 Fisher's Exact and Chi-Square contingency tests across all
    hypotheses, applying Benjamini-Hochberg FDR correction.

    Contingency Matrix:
                    Feature = v    Feature != v
    Anomaly              k_a          N_a - k_a
    Baseline             k_b          N_b - k_b

    Args:
        df_anomaly: Anomaly dataset.
        df_baseline: Continuous baseline dataset.
        alpha: Nominal p-value significance cutoff (default 0.01).
        fdr_threshold: Benjamini-Hochberg FDR q-value cutoff (default 0.05).
        target_class: Target class subset ('ALL', 'GREEN', 'RED').
        min_support: Minimum anomaly count threshold.
        discrete_cols: Optional list of discrete columns to test.

    Returns:
        pd.DataFrame sorted by q_value ascending, then Lift descending.
    """
    df_a = df_anomaly.copy()
    if target_class.upper() != "ALL":
        dir_col = "Candle_Direction" if "Candle_Direction" in df_a.columns else "Direction"
        if dir_col in df_a.columns:
            df_a = df_a[df_a[dir_col].astype(str).str.upper() == target_class.upper()].copy()

    n_a = len(df_a)
    n_b = len(df_baseline)
    if n_a == 0 or n_b == 0:
        return pd.DataFrame()

    if discrete_cols is None:
        discrete_cols = get_discrete_feature_columns(df_a)

    records = []
    p_fisher_list = []

    for col in discrete_cols:
        if col not in df_baseline.columns:
            continue

        counts_a = df_a[col].value_counts()
        counts_b = df_baseline[col].value_counts()

        for val, k_a in counts_a.items():
            if k_a < min_support:
                continue

            k_b = counts_b.get(val, 0)
            p_a = k_a / n_a
            p_b = k_b / n_b if n_b > 0 else 0.0
            lift = (p_a / p_b) if p_b > 0 else (np.inf if p_a > 0 else 0.0)

            # Build 2x2 contingency table
            table = np.array([
                [k_a, n_a - k_a],
                [k_b, n_b - k_b]
            ])

            # Fisher's Exact test
            try:
                odds_ratio, p_fisher = stats.fisher_exact(table, alternative="two-sided")
            except Exception:
                odds_ratio, p_fisher = 1.0, 1.0

            # Chi-square test with Yates continuity correction
            try:
                chi2_stat, p_chi2, dof, _ = stats.chi2_contingency(table, correction=True)
            except Exception:
                chi2_stat, p_chi2 = 0.0, 1.0

            records.append({
                "Feature": col,
                "Value": str(val),
                "Target_Class": target_class.upper(),
                "Anomaly_Count": int(k_a),
                "Anomaly_Total": int(n_a),
                "Anomaly_Prob": round(float(p_a), 6),
                "Baseline_Count": int(k_b),
                "Baseline_Total": int(n_b),
                "Baseline_Prob": round(float(p_b), 6),
                "Lift": round(float(lift), 4),
                "Odds_Ratio": round(float(odds_ratio), 4) if not np.isinf(odds_ratio) else 9999.0,
                "P_Fisher": float(p_fisher),
                "Chi2_Stat": round(float(chi2_stat), 4),
                "P_Chi2": float(p_chi2),
            })
            p_fisher_list.append(float(p_fisher))

    if not records:
        return pd.DataFrame()

    df_res = pd.DataFrame(records)

    # Benjamini-Hochberg FDR correction across all tested univariate hypotheses
    p_arr = np.array(p_fisher_list)
    p_arr = np.nan_to_num(p_arr, nan=1.0, posinf=1.0, neginf=1.0)
    reject, q_values, _, _ = multipletests(p_arr, alpha=fdr_threshold, method="fdr_bh")

    df_res["Q_Value_FDR"] = q_values
    df_res["Is_Significant_FDR"] = df_res["Q_Value_FDR"] < fdr_threshold
    df_res["Is_Significant_Nominal"] = df_res["P_Fisher"] < alpha

    # Sort by FDR Q-value ascending, then Lift descending
    df_res = df_res.sort_values(by=["Q_Value_FDR", "P_Fisher", "Lift"], ascending=[True, True, False]).reset_index(drop=True)

    return df_res


def run_continuous_distribution_tests(
    df_anomaly: pd.DataFrame,
    df_baseline: pd.DataFrame,
    target_class: str = "ALL",
    alpha: float = 0.01,
    fdr_threshold: float = 0.05,
    continuous_cols: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Executes two-sample Kolmogorov-Smirnov (KS) and Mann-Whitney U tests on all
    continuous planetary features, computing Cohen's d effect sizes and FDR q-values.

    Args:
        df_anomaly: Anomaly dataset.
        df_baseline: Baseline dataset.
        target_class: Target class ('ALL', 'GREEN', 'RED').
        alpha: Nominal p-value cutoff.
        fdr_threshold: FDR q-value cutoff.
        continuous_cols: Optional list of continuous columns to evaluate.

    Returns:
        pd.DataFrame sorted by KS_QValue ascending.
    """
    df_a = df_anomaly.copy()
    if target_class.upper() != "ALL":
        dir_col = "Candle_Direction" if "Candle_Direction" in df_a.columns else "Direction"
        if dir_col in df_a.columns:
            df_a = df_a[df_a[dir_col].astype(str).str.upper() == target_class.upper()].copy()

    if continuous_cols is None:
        continuous_cols = get_continuous_feature_columns(df_a)

    records = []
    ks_pvals = []
    mwu_pvals = []

    for col in continuous_cols:
        if col not in df_baseline.columns:
            continue

        vals_a = df_a[col].dropna().astype(float).values
        vals_b = df_baseline[col].dropna().astype(float).values

        if len(vals_a) < 5 or len(vals_b) < 5:
            continue

        mean_a, std_a = float(np.mean(vals_a)), float(np.std(vals_a, ddof=1)) if len(vals_a) > 1 else 0.0
        mean_b, std_b = float(np.mean(vals_b)), float(np.std(vals_b, ddof=1)) if len(vals_b) > 1 else 0.0
        med_a, med_b = float(np.median(vals_a)), float(np.median(vals_b))

        # Pooled Cohen's d effect size
        n1, n2 = len(vals_a), len(vals_b)
        pooled_var = (((n1 - 1) * (std_a ** 2)) + ((n2 - 1) * (std_b ** 2))) / max(n1 + n2 - 2, 1)
        pooled_std = math.sqrt(pooled_var) if pooled_var > 0 else 1e-6
        cohens_d = (mean_a - mean_b) / pooled_std

        # Two-sample KS test
        try:
            ks_res = stats.ks_2samp(vals_a, vals_b)
            ks_stat, ks_pval = float(ks_res.statistic), float(ks_res.pvalue)
        except Exception:
            ks_stat, ks_pval = 0.0, 1.0

        # Mann-Whitney U test
        try:
            mwu_res = stats.mannwhitneyu(vals_a, vals_b, alternative="two-sided")
            mwu_stat, mwu_pval = float(mwu_res.statistic), float(mwu_res.pvalue)
        except Exception:
            mwu_stat, mwu_pval = 0.0, 1.0

        records.append({
            "Feature": col,
            "Target_Class": target_class.upper(),
            "N_Anomaly": n1,
            "N_Baseline": n2,
            "Mean_Anomaly": round(mean_a, 4),
            "Std_Anomaly": round(std_a, 4),
            "Median_Anomaly": round(med_a, 4),
            "Mean_Baseline": round(mean_b, 4),
            "Std_Baseline": round(std_b, 4),
            "Median_Baseline": round(med_b, 4),
            "Cohens_D": round(cohens_d, 4),
            "KS_Stat": round(ks_stat, 4),
            "KS_PValue": ks_pval,
            "MWU_Stat": round(mwu_stat, 2),
            "MWU_PValue": mwu_pval,
        })
        ks_pvals.append(ks_pval)
        mwu_pvals.append(mwu_pval)

    if not records:
        return pd.DataFrame()

    df_cont = pd.DataFrame(records)

    # Benjamini-Hochberg FDR correction on continuous tests
    ks_arr = np.nan_to_num(np.array(ks_pvals), nan=1.0)
    mwu_arr = np.nan_to_num(np.array(mwu_pvals), nan=1.0)

    _, ks_qvals, _, _ = multipletests(ks_arr, alpha=fdr_threshold, method="fdr_bh")
    _, mwu_qvals, _, _ = multipletests(mwu_arr, alpha=fdr_threshold, method="fdr_bh")

    df_cont["KS_QValue"] = ks_qvals
    df_cont["MWU_QValue"] = mwu_qvals
    df_cont["Is_Significant_FDR"] = (df_cont["KS_QValue"] < fdr_threshold) | (df_cont["MWU_QValue"] < fdr_threshold)
    df_cont["Is_Significant_Nominal"] = (df_cont["KS_PValue"] < alpha) | (df_cont["MWU_PValue"] < alpha)

    df_cont = df_cont.sort_values(by=["KS_QValue", "KS_PValue", "MWU_QValue"], ascending=[True, True, True]).reset_index(drop=True)

    return df_cont


# ═══════════════════════════════════════════════════════════════
# R3: HIGHER-ORDER COMBINATORIAL PATTERN MINING
# ═══════════════════════════════════════════════════════════════

def _build_transaction_matrix(df: pd.DataFrame, candidate_cols: List[str]) -> pd.DataFrame:
    """Builds a binary one-hot transaction matrix for frequent itemset mining."""
    item_cols = {}
    for col in candidate_cols:
        if col not in df.columns:
            continue

        s = df[col]
        if pd.api.types.is_string_dtype(s) or pd.api.types.is_object_dtype(s) or isinstance(s.dtype, pd.CategoricalDtype):
            top_vals = s.value_counts().head(20).index
            for val in top_vals:
                item_cols[f"{col}=={val}"] = (s == val).values
        elif pd.api.types.is_numeric_dtype(s):
            u_vals = pd.unique(s.dropna())
            if len(u_vals) <= 12:
                for val in u_vals:
                    item_cols[f"{col}=={val}"] = (s == val).values

    # Add classical derived conditions
    for p in ["Moon", "Mars", "Mercury", "Venus"]:
        dec_col = f"{p}_Declination"
        if dec_col in df.columns:
            item_cols[f"{p}_OOB"] = (df[dec_col].abs() > OOB_DECLINATION_THRESHOLD).values

    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        spd_col = f"{p}_Speed"
        if spd_col in df.columns:
            item_cols[f"{p}_Stationary"] = (df[spd_col].abs() < STATIONARY_SPEED_THRESHOLD).values

    # SAV Crisis and High Support
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        sav_col = f"SAV_At_{p}"
        if sav_col in df.columns:
            item_cols[f"{p}_SAV_Crisis(<25)"] = (df[sav_col] < 25).values
            item_cols[f"{p}_SAV_Support(>32)"] = (df[sav_col] > 32).values

    return pd.DataFrame(item_cols, index=df.index)


def _evaluate_item_mask_on_df(df: pd.DataFrame, item_name: str, cache: Optional[Dict[str, np.ndarray]] = None) -> np.ndarray:
    """Evaluates an individual predicate string against a dataframe with optional caching."""
    if cache is not None and item_name in cache:
        return cache[item_name]

    n = len(df)
    res = None
    if "==" in item_name:
        col, val = item_name.split("==")
        col, val = col.strip(), val.strip()
        if col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                try:
                    num_val = float(val) if "." in val else int(val)
                    res = (df[col] == num_val).values
                except ValueError:
                    res = (df[col].astype(str) == val).values
            else:
                res = (df[col].astype(str) == val).values
    elif "_OOB" in item_name:
        p = item_name.replace("_OOB", "")
        col = f"{p}_Declination"
        if col in df.columns:
            res = (df[col].abs() > OOB_DECLINATION_THRESHOLD).values
    elif "_Stationary" in item_name:
        p = item_name.replace("_Stationary", "")
        col = f"{p}_Speed"
        if col in df.columns:
            res = (df[col].abs() < STATIONARY_SPEED_THRESHOLD).values
    elif "_SAV_Crisis(<25)" in item_name:
        p = item_name.split("_SAV_Crisis")[0]
        col = f"SAV_At_{p}"
        if col in df.columns:
            res = (df[col] < 25).values
    elif "_SAV_Support(>32)" in item_name:
        p = item_name.split("_SAV_Support")[0]
        col = f"SAV_At_{p}"
        if col in df.columns:
            res = (df[col] > 32).values
    elif item_name in df.columns:
        res = df[item_name].astype(bool).values

    if res is None:
        res = np.zeros(n, dtype=bool)

    if cache is not None:
        cache[item_name] = res
    return res


def _evaluate_antecedent_on_df(df: pd.DataFrame, items: List[str], cache: Optional[Dict[str, np.ndarray]] = None) -> np.ndarray:
    """Evaluates a conjunction of item predicates against a dataframe."""
    mask = np.ones(len(df), dtype=bool)
    for it in items:
        mask &= _evaluate_item_mask_on_df(df, it, cache=cache)
    return mask


def mine_combinatorial_patterns(
    df_anomaly: pd.DataFrame,
    df_baseline: pd.DataFrame,
    k_max: int = 4,
    min_support: int = 10,
    min_confidence: float = 0.70,
    min_lift: float = 2.0,
    max_pvalue: float = 0.005,
    target_col: str = "Candle_Direction",
    target_val: Optional[str] = None,
) -> pd.DataFrame:
    """
    Mines 2-way, 3-way, and 4-way planetary interacting rules (conjunctions)
    predicting market crashes (RED) or bullish shock breakouts (GREEN) with
    strict statistical significance thresholds.

    Rules satisfy:
      - Support N >= min_support (default 10)
      - Confidence (Purity) >= min_confidence (default 0.70)
      - Lift >= min_lift (default 2.0x)
      - Fisher Exact p-value <= max_pvalue (default 0.005)

    Args:
        df_anomaly: Anomaly dataset.
        df_baseline: Baseline dataset.
        k_max: Max conjunction order (2, 3, or 4).
        min_support: Minimum target support count.
        min_confidence: Minimum rule confidence.
        min_lift: Minimum lift multiplier.
        max_pvalue: Maximum Fisher exact p-value.
        target_col: Column containing target direction.
        target_val: Specific target ('RED', 'GREEN', or None for both).

    Returns:
        pd.DataFrame of validated combinatorial planetary rules.
    """
    if target_col not in df_anomaly.columns and "Direction" in df_anomaly.columns:
        target_col = "Direction"

    target_values = [target_val] if target_val is not None else ["RED", "GREEN"]

    # Select high-information candidate columns for conjunction mining
    candidate_cols = [
        col for col in df_anomaly.columns
        if any(col.endswith(sfx) for sfx in ["_Sign", "_Nakshatra", "_Retro", "_Combust", "_Vargottama", "_Kakshya"])
        or col.startswith("Bhv_")
        or col.startswith("Jaimini_")
        or col.startswith("Vim_")
        or col.startswith("KP_")
    ]

    logger.info(f"Building itemset transaction matrix across {len(candidate_cols)} Vedic features...")
    tx_anomaly = _build_transaction_matrix(df_anomaly, candidate_cols)

    # Build lookup dictionaries and numpy arrays
    item_names = list(tx_anomaly.columns)
    col_to_idx = {name: i for i, name in enumerate(item_names)}
    arr_a = tx_anomaly.values.astype(bool)

    # Precompute top univariate candidate items with support >= min_support
    item_counts_a = arr_a.sum(axis=0)
    viable_indices = np.where(item_counts_a >= min_support)[0]
    logger.info(f"Identified {len(viable_indices)} viable item predicates with support >= {min_support}.")

    total_anomalies = len(df_anomaly)
    total_baseline = len(df_baseline)
    discovered_rules = []
    rule_id = 1
    baseline_cache: Dict[str, np.ndarray] = {}

    date_col = "Datetime_UTC" if "Datetime_UTC" in df_anomaly.columns else None

    for t_val in target_values:
        t_mask = (df_anomaly[target_col].astype(str).str.upper() == t_val.upper())
        t_arr = t_mask.values.astype(bool)
        n_target_total = int(t_arr.sum())
        p_target_prior = n_target_total / max(total_anomalies, 1)

        if n_target_total < min_support:
            continue

        # ── 1. FP-Growth Frequent Target Itemset Mining ──
        try:
            tx_target = tx_anomaly.copy()
            tx_target[f"TARGET_{t_val}"] = t_arr

            min_sup_frac = max(min_support / total_anomalies, 0.02)
            frequent_itemsets = fpgrowth(tx_target, min_support=min_sup_frac, use_colnames=True, max_len=k_max + 1)

            if not frequent_itemsets.empty:
                target_str = f"TARGET_{t_val}"
                has_target = frequent_itemsets["itemsets"].apply(lambda x: target_str in x and len(x) >= 2)
                target_itemsets = frequent_itemsets[has_target]

                for itemset in target_itemsets["itemsets"].values:
                    ant_items = [item for item in itemset if item != target_str]
                    k_order = len(ant_items)
                    if k_order < 2 or k_order > k_max:
                        continue

                    ant_idx = [col_to_idx[item] for item in ant_items if item in col_to_idx]
                    if len(ant_idx) != len(ant_items):
                        continue

                    ant_mask_a = np.all(arr_a[:, ant_idx], axis=1)
                    k_a = int((ant_mask_a & t_arr).sum())
                    if k_a < min_support:
                        continue

                    n_match_a = int(ant_mask_a.sum())
                    conf = k_a / max(n_match_a, 1)
                    lift = conf / max(p_target_prior, 1e-6)

                    if conf >= min_confidence and lift >= min_lift:
                        c_table = np.array([
                            [k_a, n_match_a - k_a],
                            [n_target_total - k_a, (total_anomalies - n_target_total) - (n_match_a - k_a)]
                        ])
                        try:
                            _, p_fisher = stats.fisher_exact(c_table, alternative="greater")
                        except Exception:
                            p_fisher = 1.0

                        if p_fisher <= max_pvalue:
                            ant_mask_b = _evaluate_antecedent_on_df(df_baseline, ant_items, cache=baseline_cache)
                            n_match_b = int(ant_mask_b.sum())

                            dates_sample = []
                            if date_col:
                                dates_sample = df_anomaly.loc[ant_mask_a & t_arr, date_col].astype(str).head(3).tolist()

                            ant_str = " AND ".join([f"[{item}]" for item in ant_items])
                            discovered_rules.append({
                                "Rule_ID": f"RULE_FP_{rule_id:04d}",
                                "Order_K": k_order,
                                "Antecedent": ant_str,
                                "Consequent": f"Direction == {t_val}",
                                "Support_N": k_a,
                                "Total_Matches_Anomaly": n_match_a,
                                "Baseline_Matches": n_match_b,
                                "Confidence_Pct": round(conf * 100.0, 2),
                                "Lift": round(lift, 3),
                                "Fisher_PValue": float(p_fisher),
                                "Historical_Dates_Sample": ", ".join(dates_sample),
                            })
                            rule_id += 1
        except Exception as e:
            logger.warning(f"FP-Growth mining error: {e}")

        # ── 2. Vectorized Multi-Way Conjunction Mining (2-way, 3-way, 4-way) ──
        # Rank candidate items by target purity
        item_scores = []
        for idx in viable_indices:
            mask_i = arr_a[:, idx]
            k_i = int((mask_i & t_arr).sum())
            total_i = int(mask_i.sum())
            if total_i > 0:
                conf_i = k_i / total_i
                item_scores.append((idx, conf_i, k_i))

        item_scores.sort(key=lambda x: (x[1], x[2]), reverse=True)
        top_idx_list = [x[0] for x in item_scores[:35]]  # Top 35 high-conviction items

        # 2-way conjunctions
        for i_pos in range(len(top_idx_list)):
            idx1 = top_idx_list[i_pos]
            it1 = item_names[idx1]
            m1_a = arr_a[:, idx1]

            for j_pos in range(i_pos + 1, len(top_idx_list)):
                idx2 = top_idx_list[j_pos]
                it2 = item_names[idx2]
                m_pair_a = m1_a & arr_a[:, idx2]
                k_pair = int((m_pair_a & t_arr).sum())
                if k_pair < min_support:
                    continue

                total_pair_a = int(m_pair_a.sum())
                conf_pair = k_pair / max(total_pair_a, 1)
                lift_pair = conf_pair / max(p_target_prior, 1e-6)

                if conf_pair >= min_confidence and lift_pair >= min_lift:
                    c_table = np.array([
                        [k_pair, total_pair_a - k_pair],
                        [n_target_total - k_pair, (total_anomalies - n_target_total) - (total_pair_a - k_pair)]
                    ])
                    try:
                        _, p_f = stats.fisher_exact(c_table, alternative="greater")
                    except Exception:
                        p_f = 1.0

                    if p_f <= max_pvalue:
                        m_pair_b = _evaluate_item_mask_on_df(df_baseline, it1, cache=baseline_cache) & _evaluate_item_mask_on_df(df_baseline, it2, cache=baseline_cache)
                        total_pair_b = int(m_pair_b.sum())

                        dates_sample = []
                        if date_col:
                            dates_sample = df_anomaly.loc[m_pair_a & t_arr, date_col].astype(str).head(3).tolist()

                        discovered_rules.append({
                            "Rule_ID": f"RULE_2W_{rule_id:04d}",
                            "Order_K": 2,
                            "Antecedent": f"[{it1}] AND [{it2}]",
                            "Consequent": f"Direction == {t_val}",
                            "Support_N": k_pair,
                            "Total_Matches_Anomaly": total_pair_a,
                            "Baseline_Matches": total_pair_b,
                            "Confidence_Pct": round(conf_pair * 100.0, 2),
                            "Lift": round(lift_pair, 3),
                            "Fisher_PValue": float(p_f),
                            "Historical_Dates_Sample": ", ".join(dates_sample),
                        })
                        rule_id += 1

                # 3-way conjunctions
                if k_max >= 3 and i_pos < 12 and j_pos < 12:
                    for m_pos in range(j_pos + 1, min(len(top_idx_list), 18)):
                        idx3 = top_idx_list[m_pos]
                        it3 = item_names[idx3]
                        m_tri_a = m_pair_a & arr_a[:, idx3]
                        k_tri = int((m_tri_a & t_arr).sum())
                        if k_tri < min_support:
                            continue

                        total_tri_a = int(m_tri_a.sum())
                        conf_tri = k_tri / max(total_tri_a, 1)
                        lift_tri = conf_tri / max(p_target_prior, 1e-6)

                        if conf_tri >= min_confidence and lift_tri >= min_lift:
                            c_table = np.array([
                                [k_tri, total_tri_a - k_tri],
                                [n_target_total - k_tri, (total_anomalies - n_target_total) - (total_tri_a - k_tri)]
                            ])
                            try:
                                _, p_f3 = stats.fisher_exact(c_table, alternative="greater")
                            except Exception:
                                p_f3 = 1.0

                            if p_f3 <= max_pvalue:
                                m_tri_b = m_pair_b & _evaluate_item_mask_on_df(df_baseline, it3, cache=baseline_cache)
                                total_tri_b = int(m_tri_b.sum())

                                dates_sample = []
                                if date_col:
                                    dates_sample = df_anomaly.loc[m_tri_a & t_arr, date_col].astype(str).head(3).tolist()

                                discovered_rules.append({
                                    "Rule_ID": f"RULE_3W_{rule_id:04d}",
                                    "Order_K": 3,
                                    "Antecedent": f"[{it1}] AND [{it2}] AND [{it3}]",
                                    "Consequent": f"Direction == {t_val}",
                                    "Support_N": k_tri,
                                    "Total_Matches_Anomaly": total_tri_a,
                                    "Baseline_Matches": total_tri_b,
                                    "Confidence_Pct": round(conf_tri * 100.0, 2),
                                    "Lift": round(lift_tri, 3),
                                    "Fisher_PValue": float(p_f3),
                                    "Historical_Dates_Sample": ", ".join(dates_sample),
                                })
                                rule_id += 1

    df_rules = pd.DataFrame(discovered_rules)
    if not df_rules.empty:
        # Deduplicate antecedents
        df_rules = df_rules.drop_duplicates(subset=["Antecedent", "Consequent"])
        df_rules = df_rules.sort_values(by=["Lift", "Confidence_Pct", "Support_N"], ascending=[False, False, False]).reset_index(drop=True)

    return df_rules


def extract_decision_tree_rules(
    df_anomaly: pd.DataFrame,
    df_baseline: pd.DataFrame,
    max_depth: int = 4,
    min_samples_leaf: int = 10,
    target_col: str = "Candle_Direction",
) -> List[Dict[str, Any]]:
    """
    Fits shallow Decision Tree classifiers on discrete Vedic features and extracts
    intuitive, readable root-to-leaf decision rules.

    Args:
        df_anomaly: Anomaly dataset.
        df_baseline: Baseline dataset.
        max_depth: Max tree depth (default 4).
        min_samples_leaf: Minimum samples per leaf node (default 10).
        target_col: Target direction column.

    Returns:
        List of rule dictionaries with path conditions and metrics.
    """
    if target_col not in df_anomaly.columns and "Direction" in df_anomaly.columns:
        target_col = "Direction"

    candidate_cols = [
        col for col in df_anomaly.columns
        if any(col.endswith(sfx) for sfx in ["_Sign", "_Nakshatra", "_Retro", "_Combust", "_Vargottama", "_Kakshya"])
        or col.startswith("Bhv_")
        or col.startswith("Jaimini_")
        or col.startswith("Vim_")
    ]

    tx_matrix = _build_transaction_matrix(df_anomaly, candidate_cols)
    if tx_matrix.empty:
        return []

    y = (df_anomaly[target_col].astype(str).str.upper() == "RED").astype(int).values
    class_names = ["GREEN", "RED"]

    dt = DecisionTreeClassifier(
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        class_weight="balanced",
        random_state=42,
    )
    dt.fit(tx_matrix, y)

    tree_ = dt.tree_
    feature_names = tx_matrix.columns.tolist()

    rules = []

    def recurse(node: int, current_rule: List[str]):
        if tree_.feature[node] != -2:  # Not a leaf node
            feat_idx = tree_.feature[node]
            name = feature_names[feat_idx]
            threshold = tree_.threshold[node]

            # In binary matrix, <= 0.5 is False, > 0.5 is True
            recurse(tree_.children_left[node], current_rule + [f"NOT [{name}]"])
            recurse(tree_.children_right[node], current_rule + [f"[{name}]"])
        else:  # Leaf node
            counts = tree_.value[node][0]
            total_leaf = int(np.sum(counts))
            if total_leaf >= min_samples_leaf:
                predicted_class_idx = int(np.argmax(counts))
                predicted_class = class_names[predicted_class_idx]
                purity = counts[predicted_class_idx] / max(total_leaf, 1)

                if purity >= 0.65 and current_rule:
                    rule_cond = " AND ".join(current_rule)
                    rules.append({
                        "Rule_Condition": rule_cond,
                        "Predicted_Class": predicted_class,
                        "Leaf_Samples": total_leaf,
                        "Class_Distribution": {
                            "GREEN": int(counts[0]),
                            "RED": int(counts[1])
                        },
                        "Confidence_Pct": round(purity * 100.0, 2),
                    })

    recurse(0, [])
    return rules


def run_permutation_test(
    df_anomaly: pd.DataFrame,
    df_baseline: pd.DataFrame,
    rule_condition: Union[str, Dict[str, Any], Any],
    n_permutations: int = 1000,
    target_col: str = "Candle_Direction",
    target_val: str = "RED",
) -> Dict[str, Any]:
    """
    Computes a non-parametric Monte Carlo permutation test for a candidate rule,
    destroying the feature-label association to obtain an empirical p-value.

    Args:
        df_anomaly: Anomaly dataset.
        df_baseline: Baseline dataset.
        rule_condition: String antecedent (e.g. "[Mars_Retro==1] AND [Moon_Sign==Aries]").
        n_permutations: Number of random permutations (default 1000).
        target_col: Target column.
        target_val: Target class value ('RED' or 'GREEN').

    Returns:
        Dict with observed statistics, null distribution metrics, and empirical p-value.
    """
    if target_col not in df_anomaly.columns and "Direction" in df_anomaly.columns:
        target_col = "Direction"

    y_true = (df_anomaly[target_col].astype(str).str.upper() == target_val.upper()).values
    n_total = len(y_true)
    prior_prob = y_true.sum() / max(n_total, 1)

    # Evaluate rule mask on df_anomaly
    if isinstance(rule_condition, str):
        # Extract items from "[Item1] AND [Item2]"
        parts = [p.strip("[] ") for p in rule_condition.split("AND")]
        mask = np.ones(n_total, dtype=bool)
        for part in parts:
            if "==" in part:
                col, val = part.split("==")
                col, val = col.strip(), val.strip()
                if col in df_anomaly.columns:
                    mask &= (df_anomaly[col].astype(str) == val).values
            elif "_OOB" in part:
                p_name = part.replace("_OOB", "")
                col = f"{p_name}_Declination"
                if col in df_anomaly.columns:
                    mask &= (df_anomaly[col].abs() > OOB_DECLINATION_THRESHOLD).values
            elif "_Stationary" in part:
                p_name = part.replace("_Stationary", "")
                col = f"{p_name}_Speed"
                if col in df_anomaly.columns:
                    mask &= (df_anomaly[col].abs() < STATIONARY_SPEED_THRESHOLD).values
            elif col in df_anomaly.columns:
                mask &= (df_anomaly[col].astype(bool)).values
    else:
        mask = np.ones(n_total, dtype=bool)

    k_obs = int((mask & y_true).sum())
    total_match = int(mask.sum())

    if total_match == 0:
        return {
            "Rule_Condition": str(rule_condition),
            "Observed_Support": 0,
            "Observed_Confidence": 0.0,
            "Observed_Lift": 0.0,
            "Perm_Mean_Lift": 0.0,
            "Perm_Std_Lift": 0.0,
            "P_Permutation": 1.0,
            "Is_Significant": False,
        }

    obs_conf = k_obs / total_match
    obs_lift = obs_conf / max(prior_prob, 1e-6)

    # Monte Carlo permutation loop
    perm_lifts = []
    rng = np.random.default_rng(42)
    for _ in range(n_permutations):
        y_perm = rng.permutation(y_true)
        k_perm = int((mask & y_perm).sum())
        conf_perm = k_perm / total_match
        lift_perm = conf_perm / max(prior_prob, 1e-6)
        perm_lifts.append(lift_perm)

    perm_arr = np.array(perm_lifts)
    p_perm = float((np.sum(perm_arr >= obs_lift) + 1) / (n_permutations + 1))

    return {
        "Rule_Condition": str(rule_condition),
        "Observed_Support": k_obs,
        "Total_Matches": total_match,
        "Observed_Confidence_Pct": round(obs_conf * 100.0, 2),
        "Observed_Lift": round(obs_lift, 4),
        "Perm_Mean_Lift": round(float(np.mean(perm_arr)), 4),
        "Perm_Std_Lift": round(float(np.std(perm_arr)), 4),
        "P_Permutation": round(p_perm, 6),
        "Is_Significant": bool(p_perm < 0.01),
    }


# ═══════════════════════════════════════════════════════════════
# R5: 10-PILLAR FORENSIC DRILLDOWN ENGINE
# ═══════════════════════════════════════════════════════════════

def run_10_pillar_forensic_drilldown(
    df_anomaly: pd.DataFrame,
    df_baseline: pd.DataFrame,
) -> Dict[str, pd.DataFrame]:
    """
    Executes systematic hypothesis testing and builds structured statistical tables
    across all 10 Classical Vedic Astrology Pillars.

    Pillars Analyzed:
      1. Ephemeris & Declinations (OOB |delta| > 23.44 deg, Planetary Stations)
      2. Mutual Aspects & Bhavas (6/8 Shadashtaka, 2/12 Dwirdwadasa, 1/7 Samasaptaka)
      3. Divisional Vargas (D1..D60, Vargottama, Pushkara Navamsha)
      4. Jaimini Chara Karakas (GK Crash Karaka vs AK Soul/Trend Karaka)
      5. Ashtakavarga & SAV Point Thresholds (< 25 Crisis vs > 32 Support)
      6. Shadbala 6-Fold Potency & Classical Combustion
      7. Sarvatobhadra Chakra & Vedha Network (Malefic Nakshatras & Kakshyas)
      8. KP Sub-Lords & Star-Lords (NYSE Lagna & Planetary Cusps)
      9. NYSE Natal Vimshottari Dashas (MD/AD/PD cycles from 1792)
     10. Multi-Timeframe Confluence & Resonance Profiles

    Returns:
        Dict mapping Pillar name -> pd.DataFrame of statistical results.
    """
    logger.info("Executing Deep Vedic 10-Pillar Forensic Drilldown...")
    pillar_reports = {}

    # ── PILLAR 1: Ephemeris, Out-of-Bounds Declinations & Stations ──
    p1_records = []
    # Test OOB for Moon, Mars, Mercury, Venus
    for p in ["Moon", "Mars", "Mercury", "Venus"]:
        dec_col = f"{p}_Declination"
        if dec_col in df_anomaly.columns and dec_col in df_baseline.columns:
            k_a = int((df_anomaly[dec_col].abs() > OOB_DECLINATION_THRESHOLD).sum())
            k_b = int((df_baseline[dec_col].abs() > OOB_DECLINATION_THRESHOLD).sum())
            n_a, n_b = len(df_anomaly), len(df_baseline)
            p_a, p_b = k_a / n_a, k_b / n_b
            lift = p_a / max(p_b, 1e-6)
            table = np.array([[k_a, n_a - k_a], [k_b, n_b - k_b]])
            try:
                _, p_val = stats.fisher_exact(table)
            except Exception:
                p_val = 1.0

            p1_records.append({
                "Pillar": "Pillar 1 - Ephemeris",
                "Metric_Type": "Out-of-Bounds Declination (|δ| > 23.44°)",
                "Graha": p,
                "Anomaly_Count": k_a,
                "Anomaly_Pct": round(p_a * 100.0, 2),
                "Baseline_Count": k_b,
                "Baseline_Pct": round(p_b * 100.0, 2),
                "Lift": round(lift, 3),
                "Fisher_PValue": p_val,
                "Is_Significant": p_val < 0.01,
            })

    # Test Planetary Stations (|Speed| < 0.05 deg/day)
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        spd_col = f"{p}_Speed"
        if spd_col in df_anomaly.columns and spd_col in df_baseline.columns:
            k_a = int((df_anomaly[spd_col].abs() < STATIONARY_SPEED_THRESHOLD).sum())
            k_b = int((df_baseline[spd_col].abs() < STATIONARY_SPEED_THRESHOLD).sum())
            n_a, n_b = len(df_anomaly), len(df_baseline)
            p_a, p_b = k_a / n_a, k_b / n_b
            lift = p_a / max(p_b, 1e-6)
            table = np.array([[k_a, n_a - k_a], [k_b, n_b - k_b]])
            try:
                _, p_val = stats.fisher_exact(table)
            except Exception:
                p_val = 1.0

            p1_records.append({
                "Pillar": "Pillar 1 - Ephemeris",
                "Metric_Type": "Planetary Station (|Speed| < 0.05°/day)",
                "Graha": p,
                "Anomaly_Count": k_a,
                "Anomaly_Pct": round(p_a * 100.0, 2),
                "Baseline_Count": k_b,
                "Baseline_Pct": round(p_b * 100.0, 2),
                "Lift": round(lift, 3),
                "Fisher_PValue": p_val,
                "Is_Significant": p_val < 0.01,
            })
    pillar_reports["Pillar_1_Ephemeris"] = pd.DataFrame(p1_records)

    # ── PILLAR 2: Mutual Aspects & Bhavas (6/8, 2/12, 1/7, 5/9, 4/10) ──
    bhv_cols = [c for c in df_anomaly.columns if c.startswith("Bhv_")]
    p2_df = run_fdr_significance_sieve(df_anomaly, df_baseline, discrete_cols=bhv_cols, min_support=10)
    if not p2_df.empty:
        bhava_names = {
            "1": "1/1 Conjunction (Yuti)", "7": "1/7 Opposition (Samasaptaka)",
            "6": "6/8 Crisis/Friction (Shadashtaka)", "8": "6/8 Crisis/Friction (Shadashtaka)",
            "2": "2/12 Loss/Transition (Dwirdwadasa)", "12": "2/12 Loss/Transition (Dwirdwadasa)",
            "5": "5/9 Trine Fortune (Navapanchama)", "9": "5/9 Trine Fortune (Navapanchama)",
            "4": "4/10 Kendra Angle", "10": "4/10 Kendra Angle",
            "3": "3/11 Growth (Upachaya)", "11": "3/11 Growth (Upachaya)",
        }
        p2_df["Aspect_Type"] = p2_df["Value"].astype(str).map(bhava_names)
    pillar_reports["Pillar_2_Aspects"] = p2_df

    # ── PILLAR 3: Divisional Vargas (D1..D60 & Vargottama) ──
    varga_cols = [c for c in df_anomaly.columns if any(c.endswith(sfx) for sfx in ["_Vargottama", "_D9", "_D10", "_D60"])]
    p3_df = run_fdr_significance_sieve(df_anomaly, df_baseline, discrete_cols=varga_cols, min_support=10)
    pillar_reports["Pillar_3_Vargas"] = p3_df

    # ── PILLAR 4: Jaimini Chara Karakas (AK vs GK activations) ──
    jaimini_cols = [c for c in df_anomaly.columns if c.startswith("Jaimini_") and not c.endswith("_Deg")]
    p4_df = run_fdr_significance_sieve(df_anomaly, df_baseline, discrete_cols=jaimini_cols, min_support=10)
    pillar_reports["Pillar_4_Jaimini"] = p4_df

    # ── PILLAR 5: Ashtakavarga & SAV Points ──
    sav_cols = [c for c in df_anomaly.columns if c.startswith("SAV_")]
    p5_df = run_continuous_distribution_tests(df_anomaly, df_baseline, continuous_cols=sav_cols)
    pillar_reports["Pillar_5_Ashtakavarga"] = p5_df

    # ── PILLAR 6: Shadbala 6-Fold Potency & Combustion ──
    sb_cols = [c for c in df_anomaly.columns if c.startswith("Shadbala_")]
    p6_cont = run_continuous_distribution_tests(df_anomaly, df_baseline, continuous_cols=sb_cols)
    combust_cols = [c for c in df_anomaly.columns if c.endswith("_Combust")]
    p6_comb = run_fdr_significance_sieve(df_anomaly, df_baseline, discrete_cols=combust_cols, min_support=5)
    pillar_reports["Pillar_6_Shadbala_Continuous"] = p6_cont
    pillar_reports["Pillar_6_Combustion"] = p6_comb

    # ── PILLAR 7: Sarvatobhadra Chakra & Vedha Network (Nakshatras & Kakshyas) ──
    p7_cols = [c for c in df_anomaly.columns if c.endswith("_Nakshatra") or c.endswith("_Kakshya")]
    p7_df = run_fdr_significance_sieve(df_anomaly, df_baseline, discrete_cols=p7_cols, min_support=10)
    pillar_reports["Pillar_7_SBC_Vedha"] = p7_df

    # ── PILLAR 8: KP Sub-Lords & Star-Lords ──
    kp_cols = [c for c in df_anomaly.columns if c.startswith("KP_")]
    p8_df = run_fdr_significance_sieve(df_anomaly, df_baseline, discrete_cols=kp_cols, min_support=5)
    pillar_reports["Pillar_8_KP_SubLords"] = p8_df

    # ── PILLAR 9: NYSE Natal Vimshottari Dashas ──
    vim_cols = [c for c in df_anomaly.columns if c.startswith("Vim_")]
    p9_df = run_fdr_significance_sieve(df_anomaly, df_baseline, discrete_cols=vim_cols, min_support=5)
    pillar_reports["Pillar_9_Vimshottari"] = p9_df

    # ── PILLAR 10: Multi-Timeframe Confluence & Resonance Profiles ──
    p10_records = []
    if "MTF_Confluence_Count" in df_anomaly.columns:
        mtf_counts = df_anomaly["MTF_Confluence_Count"].value_counts().to_dict()
        for count_val, k_val in sorted(mtf_counts.items()):
            p10_records.append({
                "Confluence_Level": f"{count_val}-Timeframe Simultaneous Confluence",
                "Anomaly_Bars_Count": k_val,
                "Pct_Of_All_Anomalies": round((k_val / len(df_anomaly)) * 100.0, 2),
            })
    pillar_reports["Pillar_10_MTF_Confluence"] = pd.DataFrame(p10_records)

    logger.info("Deep Vedic 10-Pillar Forensic Drilldown complete.")
    return pillar_reports


# ═══════════════════════════════════════════════════════════════
# MASTER PIPELINE COORDINATOR
# ═══════════════════════════════════════════════════════════════

def run_full_vedic_mining_pipeline(
    anomaly_parquet: Optional[str] = None,
    baseline_parquet: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Executes the entire end-to-end Statistical Significance Sieve and Combinatorial
    Pattern Mining pipeline, generating all discovery artifacts.

    Args:
        anomaly_parquet: Path to master anomaly supreme dataset.
        baseline_parquet: Path to RTH baseline dataset.
        output_dir: Output directory for reports and tables.

    Returns:
        Dict summarizing discovery counts and findings.
    """
    if anomaly_parquet is None:
        anomaly_parquet = os.path.join(_ROOT_DIR, "data", "spy_anomalies_omni_vedic_supreme.parquet")
    if baseline_parquet is None:
        baseline_parquet = os.path.join(_ROOT_DIR, "data", "spy_continuous_rth_omni_vedic_baseline.parquet")
    if output_dir is None:
        output_dir = os.path.join(_ROOT_DIR, "reports")

    os.makedirs(output_dir, exist_ok=True)

    logger.info("=" * 70)
    logger.info("STARTING MASTER VEDIC PATTERN MINING & STATISTICAL SIEVE")
    logger.info("=" * 70)

    # 1. Load Anomaly Dataset
    df_anomaly = pd.read_parquet(anomaly_parquet)
    logger.info(f"Loaded Anomaly Dataset: {df_anomaly.shape} from {anomaly_parquet}")

    # 2. Load or Generate Baseline Dataset
    df_baseline = generate_rth_baseline_dataset(output_parquet=baseline_parquet)
    logger.info(f"Baseline Dataset ready: {df_baseline.shape}")

    # 3. Univariate Lift and FDR Sieve
    logger.info("Executing Univariate FDR Significance Sieve (q < 0.05 / p < 0.01)...")
    df_fdr_all = run_fdr_significance_sieve(df_anomaly, df_baseline, target_class="ALL")
    df_fdr_red = run_fdr_significance_sieve(df_anomaly, df_baseline, target_class="RED")
    df_fdr_green = run_fdr_significance_sieve(df_anomaly, df_baseline, target_class="GREEN")

    # 4. Continuous KS and Mann-Whitney U tests
    logger.info("Executing Continuous KS & Mann-Whitney U Distribution Tests...")
    df_cont_all = run_continuous_distribution_tests(df_anomaly, df_baseline, target_class="ALL")

    # 5. Higher-Order Combinatorial Mining (FP-Growth & Conjunctions)
    logger.info("Mining 2/3/4-Way Higher-Order Planetary Conjunctions...")
    df_rules = mine_combinatorial_patterns(
        df_anomaly, df_baseline,
        k_max=4,
        min_support=10,
        min_confidence=0.70,
        min_lift=2.0,
        max_pvalue=0.005,
    )

    # 6. Decision Tree Rule Extraction
    logger.info("Extracting Shallow Decision Tree Boundary Rules...")
    dt_rules = extract_decision_tree_rules(df_anomaly, df_baseline, max_depth=4, min_samples_leaf=10)

    # 7. Permutation Testing on Top Discovered Rules
    logger.info("Running Non-Parametric Permutation Tests (N=1000)...")
    perm_results = []
    if not df_rules.empty:
        top_rules = df_rules.head(10)
        for _, r in top_rules.iterrows():
            p_res = run_permutation_test(
                df_anomaly, df_baseline,
                rule_condition=r["Antecedent"],
                n_permutations=1000,
                target_val="RED" if "RED" in r["Consequent"] else "GREEN",
            )
            p_res["Rule_ID"] = r["Rule_ID"]
            perm_results.append(p_res)

    # 8. Deep 10-Pillar Forensic Drilldown
    drilldown = run_10_pillar_forensic_drilldown(df_anomaly, df_baseline)

    summary = {
        "anomaly_bars": len(df_anomaly),
        "baseline_bars": len(df_baseline),
        "fdr_significant_all_count": int(df_fdr_all["Is_Significant_FDR"].sum()) if not df_fdr_all.empty else 0,
        "fdr_significant_red_count": int(df_fdr_red["Is_Significant_FDR"].sum()) if not df_fdr_red.empty else 0,
        "fdr_significant_green_count": int(df_fdr_green["Is_Significant_FDR"].sum()) if not df_fdr_green.empty else 0,
        "continuous_significant_count": int(df_cont_all["Is_Significant_FDR"].sum()) if not df_cont_all.empty else 0,
        "combinatorial_rules_count": len(df_rules),
        "decision_tree_rules_count": len(dt_rules),
        "permutation_tested_count": len(perm_results),
        "pillars_evaluated": len(drilldown),
    }

    logger.info(f"Vedic Pattern Mining Pipeline Complete: {summary}")
    return {
        "summary": summary,
        "df_fdr_all": df_fdr_all,
        "df_fdr_red": df_fdr_red,
        "df_fdr_green": df_fdr_green,
        "df_cont_all": df_cont_all,
        "df_rules": df_rules,
        "dt_rules": dt_rules,
        "perm_results": perm_results,
        "drilldown": drilldown,
    }


# ═══════════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    run_full_vedic_mining_pipeline()
