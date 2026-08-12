"""
FABLE 9-POINT GRINDER
=====================
Physical-reality stress test for a reported 1.91 Sharpe.
Pure numpy/pandas. No excuses, no survivorship, no smoothing.

Points covered per spec:
  1. Incremental Sharpe vs 60/20/20 base
  2. Deflated Sharpe Ratio (Bailey & Lopez de Prado), N=12 trials
  3. 20-day Block-Bootstrap Monte Carlo (1000 paths, 5th pct Sharpe)
  4. BTC Drift Haircut -> 10% annualized CAGR, vol preserved
  5. Regime slice Sharpes
  6. Cold Start Sharpe (post 2018-01-01)
"""

import numpy as np
import pandas as pd
from math import erf, sqrt, log, exp

TRADING_DAYS = 252
EULER_GAMMA = 0.5772156649015329


# ----------------------------------------------------------------------
# Low-level stats (no scipy dependency)
# ----------------------------------------------------------------------
def _norm_cdf(x):
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def _norm_ppf(p):
    """Acklam's inverse normal CDF approximation (~1e-9 accuracy)."""
    if not (0.0 < p < 1.0):
        return np.inf if p >= 1.0 else -np.inf
    a = [-3.969683028665376e+01,  2.209460984245205e+02, -2.759285104469687e+02,
          1.383577518672690e+02, -3.066479806614716e+01,  2.506628277459239e+00]
    b = [-5.447609879822406e+01,  1.615858368580409e+02, -1.556989798598866e+02,
          6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00,  4.374664141464968e+00,  2.938163982698783e+00]
    d = [ 7.784695709041462e-03,  3.224671290700398e-01,  2.445134137142996e+00,
          3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = sqrt(-2 * log(p))
        return (((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / \
               ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1)
    if p > phigh:
        q = sqrt(-2 * log(1 - p))
        return -(((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / \
                ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r + a[1])*r + a[2])*r + a[3])*r + a[4])*r + a[5]) * q / \
           (((((b[0]*r + b[1])*r + b[2])*r + b[3])*r + b[4])*r + 1)


def sharpe(ret, ann=TRADING_DAYS):
    """Annualized Sharpe. Returns NaN if degenerate."""
    r = np.asarray(ret, dtype=float)
    r = r[~np.isnan(r)]
    if r.size < 2:
        return np.nan
    s = r.std(ddof=1)
    if s == 0:
        return np.nan
    return (r.mean() / s) * np.sqrt(ann)


def _skew_kurt(r):
    """Sample skewness and raw (non-excess) kurtosis."""
    r = np.asarray(r, dtype=float)
    mu, sd = r.mean(), r.std(ddof=0)
    if sd == 0:
        return 0.0, 3.0
    z = (r - mu) / sd
    return float(np.mean(z**3)), float(np.mean(z**4))


# ----------------------------------------------------------------------
# Point 1: Incremental Sharpe
# ----------------------------------------------------------------------
def incremental_sharpe(port_ret, base_ret):
    """
    Sharpe of the active spread (port - beta * base), aligned on common dates.
    This calculates the Appraisal Ratio.
    """
    df = pd.concat([port_ret.rename("p"), base_ret.rename("b")], axis=1).dropna()
    var_b = np.var(df["b"], ddof=1)
    beta = np.cov(df["p"], df["b"], ddof=1)[0, 1] / var_b if var_b > 0 else 0.0
    active = df["p"] - beta * df["b"]
    return {
        "port_sharpe": sharpe(df["p"]),
        "base_sharpe": sharpe(df["b"]),
        "active_sharpe": sharpe(active),
        "corr_to_base": float(df["p"].corr(df["b"])),
        "n_days": int(len(df)),
    }


# ----------------------------------------------------------------------
# Point 2: Deflated Sharpe Ratio (N=12 trials)
# ----------------------------------------------------------------------
def deflated_sharpe_ratio(ret, n_trials=12):
    """
    Bailey & Lopez de Prado (2014).
    """
    r = np.asarray(ret.dropna(), dtype=float)
    T = r.size
    sd = r.std(ddof=1)
    if T < 3 or sd == 0:
        return {"dsr": np.nan}
    sr_daily = r.mean() / sd
    g3, g4 = _skew_kurt(r)

    # Std error of the SR estimator (per-period)
    sr_var_time = (1.0 - g3 * sr_daily + ((g4 - 1.0) / 4.0) * sr_daily**2) / (T - 1)
    sr_std_time = sqrt(max(sr_var_time, 1e-18))

    # Cross-sectional variance of trials (assume 0.5 annualized standard deviation -> daily)
    sr_std_cross = 0.5 / sqrt(TRADING_DAYS)

    # Expected max of N iid null-SR draws (Gumbel approximation) using CROSS-SECTIONAL variance
    z1 = _norm_ppf(1.0 - 1.0 / n_trials)
    z2 = _norm_ppf(1.0 - 1.0 / (n_trials * np.e))
    sr0 = sr_std_cross * ((1.0 - EULER_GAMMA) * z1 + EULER_GAMMA * z2)

    dsr = _norm_cdf((sr_daily - sr0) / sr_std_time)
    return {
        "observed_sharpe_ann": sr_daily * sqrt(TRADING_DAYS),
        "sr0_hurdle_ann": sr0 * sqrt(TRADING_DAYS),
        "skew": g3,
        "kurtosis": g4,
        "n_trials": n_trials,
        "dsr": float(dsr),
        "verdict": "PASS (>0.95)" if dsr > 0.95 else "FAIL / SUSPECT",
    }


# ----------------------------------------------------------------------
# Point 3: 20-day Block-Bootstrap Monte Carlo
# ----------------------------------------------------------------------
def block_bootstrap_sharpe(ret, block=20, n_paths=1000, seed=42):
    """
    Stationary block bootstrap (non-circular) to prevent future-to-past splicing.
    """
    r = np.asarray(ret.dropna(), dtype=float)
    T = r.size
    rng = np.random.default_rng(seed)
    n_blocks = int(np.ceil(T / block))

    starts = rng.integers(0, max(1, T - block + 1), size=(n_paths, n_blocks))
    offsets = np.arange(block)
    idx = starts[:, :, None] + offsets[None, None, :]
    paths = r[idx].reshape(n_paths, -1)[:, :T]

    mu = paths.mean(axis=1)
    sd = paths.std(axis=1, ddof=1)
    srs = np.where(sd > 0, mu / sd, np.nan) * sqrt(TRADING_DAYS)
    srs = srs[~np.isnan(srs)]

    return {
        "boot_sharpe_mean": float(np.mean(srs)),
        "boot_sharpe_p05": float(np.percentile(srs, 5)),
        "boot_sharpe_p50": float(np.percentile(srs, 50)),
        "boot_sharpe_p95": float(np.percentile(srs, 95)),
        "prob_sharpe_below_zero": float(np.mean(srs < 0)),
        "n_paths": int(len(srs)),
        "block_days": block,
    }


# ----------------------------------------------------------------------
# Point 4: BTC Drift Haircut -> 10% CAGR, vol preserved
# ----------------------------------------------------------------------
def drift_haircut(port_ret, btc_ret, target_cagr=0.10):
    """
    Scaling math:
      Apply an additive shift in arithmetic linear space to preserve
      variance identically.
    """
    df = pd.concat([port_ret.rename("p"), btc_ret.rename("b")], axis=1).dropna()
    b = df["b"].values
    
    # Calculate geometric mean to find shift needed for target CAGR
    mu_hat_geom = log(np.prod(1.0 + b)) / (len(b) / TRADING_DAYS) if len(b) > 0 else 0
    mu_target_geom = target_cagr
    shift = (mu_target_geom - mu_hat_geom) / TRADING_DAYS

    btc_hc = b + shift # Preserve linear variance perfectly
    delta = btc_hc - b

    # Portfolio beta to BTC (vectorized OLS)
    p = df["p"].values
    var_b = np.var(b, ddof=1)
    beta = np.cov(p, b, ddof=1)[0, 1] / var_b if var_b > 0 else 0.0

    port_hc = p + beta * delta

    return {
        "btc_realized_cagr": float(np.prod(1.0 + b)**(TRADING_DAYS/len(b)) - 1.0),
        "target_cagr": target_cagr,
        "daily_log_drift_shift": float(shift),
        "port_beta_to_btc": float(beta),
        "sharpe_original": sharpe(p),
        "sharpe_haircut": sharpe(port_hc),
        "haircut_btc_sharpe": sharpe(btc_hc),
    }


# ----------------------------------------------------------------------
# Points 5 & 6: Regime Slices + Cold Start
# ----------------------------------------------------------------------
REGIMES = {
    "2014-2017": ("2014-01-01", "2017-12-31"),
    "2018-2019": ("2018-01-01", "2019-12-31"),
    "2020-2021": ("2020-01-01", "2021-12-31"),
    "2022":      ("2022-01-01", "2022-12-31"),
    "2023-2024": ("2023-01-01", "2024-12-31"),
}


def regime_slices(ret):
    out = {}
    for name, (lo, hi) in REGIMES.items():
        sl = ret.loc[lo:hi].dropna()
        out[name] = {"sharpe": sharpe(sl), "n_days": int(len(sl))}
    return out


def cold_start_sharpe(ret, start="2018-01-01"):
    sl = ret.loc[start:].dropna()
    return {"sharpe_post_2018": sharpe(sl), "n_days": int(len(sl))}


# ----------------------------------------------------------------------
# THE GRINDER
# ----------------------------------------------------------------------
def run_fable_grinder(port_ret_series, btc_ret_series, base_60_20_20_ret_series):
    """
    Feed it daily return Series (datetime index). It feeds back the truth.
    """
    port = port_ret_series.sort_index().astype(float)
    btc = btc_ret_series.sort_index().astype(float)
    base = base_60_20_20_ret_series.sort_index().astype(float)

    results = {
        "0_headline_sharpe": sharpe(port.dropna()),
        "1_incremental_sharpe": incremental_sharpe(port, base),
        "2_deflated_sharpe": deflated_sharpe_ratio(port, n_trials=12),
        "3_block_bootstrap": block_bootstrap_sharpe(port, block=20, n_paths=1000),
        "4_drift_haircut": drift_haircut(port, btc, target_cagr=0.10),
        "5_regime_slices": regime_slices(port),
        "6_cold_start": cold_start_sharpe(port, "2018-01-01"),
    }

    # ------------------------------------------------------------------
    # Verdict logic: the Sharpe is "physically real" only if it survives
    # deflation, the bootstrap floor, the drift haircut, and cold start.
    # ------------------------------------------------------------------
    dsr_ok = results["2_deflated_sharpe"].get("dsr", 0) > 0.95
    boot_ok = results["3_block_bootstrap"]["boot_sharpe_p05"] > 0.0
    haircut_ok = results["4_drift_haircut"]["sharpe_haircut"] > 0.5
    cold_ok = (results["6_cold_start"]["sharpe_post_2018"] or 0) > 0.5
    regime_vals = [v["sharpe"] for v in results["5_regime_slices"].values()
                   if not np.isnan(v["sharpe"])]
    regime_ok = len(regime_vals) > 0 and min(regime_vals) > 0.0

    checks = {
        "dsr_above_0.95": dsr_ok,
        "bootstrap_p05_positive": boot_ok,
        "survives_drift_haircut": haircut_ok,
        "cold_start_holds": cold_ok,
        "no_negative_regime": regime_ok,
    }
    results["7_checks"] = checks
    results["8_verdict"] = (
        "PHYSICALLY REAL — the 1.91 survives the grinder."
        if all(checks.values())
        else "MIRAGE RISK — Sharpe fails one or more physical-reality gates: "
             + ", ".join(k for k, v in checks.items() if not v)
    )

    _print_report(results)
    return results


# ----------------------------------------------------------------------
# Report printer
# ----------------------------------------------------------------------
def _print_report(res):
    ln = "=" * 64
    print(ln)
    print("FABLE 9-POINT GRINDER — RESULTS")
    print(ln)
    print(f"Headline Sharpe (full sample) : {res['0_headline_sharpe']:.3f}\n")

    inc = res["1_incremental_sharpe"]
    print("[1] INCREMENTAL SHARPE vs 60/20/20")
    print(f"    Port {inc['port_sharpe']:.3f} | Base {inc['base_sharpe']:.3f} | "
          f"Active {inc['active_sharpe']:.3f} | Corr {inc['corr_to_base']:.3f}\n")

    d = res["2_deflated_sharpe"]
    print("[2] DEFLATED SHARPE RATIO (N=12 trials)")
    print(f"    Hurdle SR0 {d['sr0_hurdle_ann']:.3f} | skew {d['skew']:.2f} | "
          f"kurt {d['kurtosis']:.2f}")
    print(f"    DSR = {d['dsr']:.4f}  -> {d['verdict']}\n")

    b = res["3_block_bootstrap"]
    print("[3] BLOCK BOOTSTRAP (20d blocks x 1000 paths)")
    print(f"    p05 {b['boot_sharpe_p05']:.3f} | p50 {b['boot_sharpe_p50']:.3f} | "
          f"p95 {b['boot_sharpe_p95']:.3f} | P(SR<0) {b['prob_sharpe_below_zero']:.3%}\n")

    h = res["4_drift_haircut"]
    print("[4] BTC DRIFT HAIRCUT -> 10% CAGR (vol preserved)")
    print(f"    Realized BTC CAGR {h['btc_realized_cagr']:.1%} | "
          f"beta {h['port_beta_to_btc']:.3f}")
    print(f"    Sharpe: {h['sharpe_original']:.3f} -> {h['sharpe_haircut']:.3f}\n")

    print("[5] REGIME SLICES")
    for k, v in res["5_regime_slices"].items():
        sr = v["sharpe"]
        s = f"{sr:.3f}" if not np.isnan(sr) else "  n/a"
        print(f"    {k:<10} SR {s:>7}  ({v['n_days']} days)")
    print()

    c = res["6_cold_start"]
    print(f"[6] COLD START (post 2018-01-01): SR {c['sharpe_post_2018']:.3f} "
          f"({c['n_days']} days)\n")

    print(ln)
    print("VERDICT:", res["8_verdict"])
    print(ln)


# ----------------------------------------------------------------------
# Self-test with synthetic data (runs only if executed directly)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    rng = np.random.default_rng(7)
    idx = pd.bdate_range("2014-01-01", "2024-12-31")
    T = len(idx)
    btc = pd.Series(rng.normal(0.0018, 0.04, T), index=idx)
    base = pd.Series(rng.normal(0.0003, 0.007, T), index=idx)
    port = 0.25 * btc + 0.6 * base + pd.Series(rng.normal(0.0002, 0.004, T), index=idx)
    run_fable_grinder(port, btc, base)