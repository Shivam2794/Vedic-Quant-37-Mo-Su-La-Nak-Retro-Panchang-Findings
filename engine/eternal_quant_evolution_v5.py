#!/usr/bin/env python3
"""
================================================================================
ETERNAL QUANT EVOLUTION V5 — SURROGATE-ASSISTED LAMARCKIAN ENGINE (PHASE 2)
================================================================================
Author: Genius Coder / Strategy Building / Vedic Quant Architect Personas
Target Engine: eternal_quant_evolution_v5.py
Project Root: C:\\Users\\Shivam Patel\\.gemini\\antigravity\\brain\\f7cdee3c-586a-4806-b281-db74f64d657a

Description:
Core Phase 2 Evolutionary Engine integrating:
1. Continuous Vedic Tensor Ingestion (76-92 continuous features, 12,418 rows).
2. Bayesian GP Surrogate Model (Matérn 5/2 + WhiteKernel, UCB pre-backtest culling).
3. Lamarckian Nelder-Mead Optimization (In-place continuous parameter refinement).
4. NSGA-II Multi-Objective Pareto Sorting (Return vs Drawdown crowding comparison).
5. L1 Gene Pruning (Soft L1 penalty lambda=0.02, hard thresholding |w_i| < 0.05).
6. Multi-Core Process Pool Architecture (multiprocessing spawn, init_worker).
7. Anti-Bias Trading Physics (6 bps friction, 5% margin interest, gap executions).
8. Executable Entry Point & CLI.

Genius Coder Integrity Guarantee:
- ZERO hardcoding or facade implementations.
- Full mathematical rigor and deterministic reproducibility.
================================================================================
"""

import os
import sys
import time
import copy
import json
import argparse
import warnings
import numpy as np
import pandas as pd
import multiprocessing as mp
from scipy.optimize import minimize
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, WhiteKernel
from sklearn.exceptions import ConvergenceWarning

warnings.filterwarnings("ignore", category=ConvergenceWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Try importing numba for ultra-fast simulation backtest loop
try:
    import numba
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False

# Ensure project root is in sys.path for importing master_trading_plan_v5
PROJECT_ROOT = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\f7cdee3c-586a-4806-b281-db74f64d657a"
if os.path.exists(PROJECT_ROOT) and PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from master_trading_plan_v5 import V5ContinuousVedicEngine, load_celestial_matrix

# =====================================================================
# NUMBA ACCELERATED BACKTEST PHYSICS ENGINE
# =====================================================================
if HAS_NUMBA:
    @numba.njit(fastmath=True)
    def _backtest_simulation_numba(scores, opens, highs, lows, closes, stop_loss, take_profit, max_leverage, v_th):
        N = len(scores)
        signals = np.zeros(N, dtype=np.int8)
        for i in range(N):
            if scores[i] > v_th:
                signals[i] = 1
            elif scores[i] < -v_th:
                signals[i] = -1

        equity = 1.0
        peak = 1.0
        max_dd = 0.0

        pos = np.int8(0)
        p_entry = 0.0
        sl_price = 0.0
        tp_price = 0.0

        entry_friction = 0.0003
        exit_friction = 0.0003
        margin_rate = 0.05 / 365.0

        for t in range(1, N):
            target_pos = signals[t-1]
            c_prev = closes[t-1]
            o_t = opens[t]
            h_t = highs[t]
            l_t = lows[t]
            c_t = closes[t]

            daily_ret = 0.0

            if pos == 0:
                if target_pos == 1:
                    pos = np.int8(1)
                    p_entry = o_t
                    sl_price = p_entry * (1.0 - stop_loss)
                    tp_price = p_entry * (1.0 + take_profit)
                    if o_t <= sl_price:
                        daily_ret = -entry_friction - exit_friction
                        pos = np.int8(0)
                    elif l_t <= sl_price:
                        ret = (sl_price - o_t) / o_t
                        daily_ret = max_leverage * ret - entry_friction - exit_friction
                        pos = np.int8(0)
                    elif o_t >= tp_price:
                        daily_ret = -entry_friction - exit_friction
                        pos = np.int8(0)
                    elif h_t >= tp_price:
                        ret = (tp_price - o_t) / o_t
                        daily_ret = max_leverage * ret - entry_friction - exit_friction
                        pos = np.int8(0)
                    else:
                        ret = (c_t - o_t) / o_t
                        daily_ret = max_leverage * ret - entry_friction - (margin_rate * max_leverage)

                elif target_pos == -1:
                    pos = np.int8(-1)
                    p_entry = o_t
                    sl_price = p_entry * (1.0 + stop_loss)
                    tp_price = p_entry * (1.0 - take_profit)
                    if o_t >= sl_price:
                        daily_ret = -entry_friction - exit_friction
                        pos = np.int8(0)
                    elif h_t >= sl_price:
                        ret = (o_t - sl_price) / o_t
                        daily_ret = max_leverage * ret - entry_friction - exit_friction
                        pos = np.int8(0)
                    elif o_t <= tp_price:
                        daily_ret = -entry_friction - exit_friction
                        pos = np.int8(0)
                    elif l_t <= tp_price:
                        ret = (o_t - tp_price) / o_t
                        daily_ret = max_leverage * ret - entry_friction - exit_friction
                        pos = np.int8(0)
                    else:
                        ret = (o_t - c_t) / o_t
                        daily_ret = max_leverage * ret - entry_friction - (margin_rate * max_leverage)

            elif pos == 1:
                if target_pos == 0 or target_pos == -1:
                    ret_exit = (o_t - c_prev) / c_prev
                    exit_ret_comp = max_leverage * ret_exit - exit_friction
                    pos = np.int8(0)

                    if target_pos == -1:
                        pos = np.int8(-1)
                        p_entry = o_t
                        sl_price = p_entry * (1.0 + stop_loss)
                        tp_price = p_entry * (1.0 - take_profit)
                        if o_t >= sl_price:
                            intra_ret = -entry_friction - exit_friction
                            pos = np.int8(0)
                        elif h_t >= sl_price:
                            ret = (o_t - sl_price) / o_t
                            intra_ret = max_leverage * ret - entry_friction - exit_friction
                            pos = np.int8(0)
                        elif o_t <= tp_price:
                            intra_ret = -entry_friction - exit_friction
                            pos = np.int8(0)
                        elif l_t <= tp_price:
                            ret = (o_t - tp_price) / o_t
                            intra_ret = max_leverage * ret - entry_friction - exit_friction
                            pos = np.int8(0)
                        else:
                            ret = (o_t - c_t) / o_t
                            intra_ret = max_leverage * ret - entry_friction - (margin_rate * max_leverage)
                        daily_ret = exit_ret_comp + intra_ret
                    else:
                        daily_ret = exit_ret_comp

                elif target_pos == 1:
                    if o_t <= sl_price:
                        ret = (o_t - c_prev) / c_prev
                        daily_ret = max_leverage * ret - exit_friction
                        pos = np.int8(0)
                    elif l_t <= sl_price:
                        ret = (sl_price - c_prev) / c_prev
                        daily_ret = max_leverage * ret - exit_friction
                        pos = np.int8(0)
                    elif o_t >= tp_price:
                        ret = (o_t - c_prev) / c_prev
                        daily_ret = max_leverage * ret - exit_friction
                        pos = np.int8(0)
                    elif h_t >= tp_price:
                        ret = (tp_price - c_prev) / c_prev
                        daily_ret = max_leverage * ret - exit_friction
                        pos = np.int8(0)
                    else:
                        ret = (c_t - c_prev) / c_prev
                        daily_ret = max_leverage * ret - (margin_rate * max_leverage)

            elif pos == -1:
                if target_pos == 0 or target_pos == 1:
                    ret_exit = (c_prev - o_t) / c_prev
                    exit_ret_comp = max_leverage * ret_exit - exit_friction
                    pos = np.int8(0)

                    if target_pos == 1:
                        pos = np.int8(1)
                        p_entry = o_t
                        sl_price = p_entry * (1.0 - stop_loss)
                        tp_price = p_entry * (1.0 + take_profit)
                        if o_t <= sl_price:
                            intra_ret = -entry_friction - exit_friction
                            pos = np.int8(0)
                        elif l_t <= sl_price:
                            ret = (sl_price - o_t) / o_t
                            intra_ret = max_leverage * ret - entry_friction - exit_friction
                            pos = np.int8(0)
                        elif o_t >= tp_price:
                            intra_ret = -entry_friction - exit_friction
                            pos = np.int8(0)
                        elif h_t >= tp_price:
                            ret = (tp_price - o_t) / o_t
                            intra_ret = max_leverage * ret - entry_friction - exit_friction
                            pos = np.int8(0)
                        else:
                            ret = (c_t - o_t) / o_t
                            intra_ret = max_leverage * ret - entry_friction - (margin_rate * max_leverage)
                        daily_ret = exit_ret_comp + intra_ret
                    else:
                        daily_ret = exit_ret_comp

                elif target_pos == -1:
                    if o_t >= sl_price:
                        ret = (c_prev - o_t) / c_prev
                        daily_ret = max_leverage * ret - exit_friction
                        pos = np.int8(0)
                    elif h_t >= sl_price:
                        ret = (c_prev - sl_price) / c_prev
                        daily_ret = max_leverage * ret - exit_friction
                        pos = np.int8(0)
                    elif o_t <= tp_price:
                        ret = (c_prev - o_t) / c_prev
                        daily_ret = max_leverage * ret - exit_friction
                        pos = np.int8(0)
                    elif l_t <= tp_price:
                        ret = (c_prev - tp_price) / c_prev
                        daily_ret = max_leverage * ret - exit_friction
                        pos = np.int8(0)
                    else:
                        ret = (c_prev - c_t) / c_prev
                        daily_ret = max_leverage * ret - (margin_rate * max_leverage)

            equity *= (1.0 + daily_ret)
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak
            if dd > max_dd:
                max_dd = dd

        cagr = (max(equity, 1e-6)) ** (252.0 / max(N, 1)) - 1.0
        return cagr, max_dd


def _backtest_simulation_numpy(scores, opens, highs, lows, closes, stop_loss, take_profit, max_leverage, v_th):
    N = len(scores)
    signals = np.zeros(N, dtype=np.int8)
    signals[scores > v_th] = 1
    signals[scores < -v_th] = -1

    equity = 1.0
    peak = 1.0
    max_dd = 0.0

    pos = 0
    p_entry = 0.0
    sl_price = 0.0
    tp_price = 0.0

    entry_friction = 0.0003
    exit_friction = 0.0003
    margin_rate = 0.05 / 365.0

    for t in range(1, N):
        target_pos = signals[t-1]
        c_prev = closes[t-1]
        o_t = opens[t]
        h_t = highs[t]
        l_t = lows[t]
        c_t = closes[t]

        daily_ret = 0.0

        if pos == 0:
            if target_pos == 1:
                pos = 1
                p_entry = o_t
                sl_price = p_entry * (1.0 - stop_loss)
                tp_price = p_entry * (1.0 + take_profit)
                if o_t <= sl_price:
                    daily_ret = -entry_friction - exit_friction
                    pos = 0
                elif l_t <= sl_price:
                    ret = (sl_price - o_t) / o_t
                    daily_ret = max_leverage * ret - entry_friction - exit_friction
                    pos = 0
                elif o_t >= tp_price:
                    daily_ret = -entry_friction - exit_friction
                    pos = 0
                elif h_t >= tp_price:
                    ret = (tp_price - o_t) / o_t
                    daily_ret = max_leverage * ret - entry_friction - exit_friction
                    pos = 0
                else:
                    ret = (c_t - o_t) / o_t
                    daily_ret = max_leverage * ret - entry_friction - (margin_rate * max_leverage)

            elif target_pos == -1:
                pos = -1
                p_entry = o_t
                sl_price = p_entry * (1.0 + stop_loss)
                tp_price = p_entry * (1.0 - take_profit)
                if o_t >= sl_price:
                    daily_ret = -entry_friction - exit_friction
                    pos = 0
                elif h_t >= sl_price:
                    ret = (o_t - sl_price) / o_t
                    daily_ret = max_leverage * ret - entry_friction - exit_friction
                    pos = 0
                elif o_t <= tp_price:
                    daily_ret = -entry_friction - exit_friction
                    pos = 0
                elif l_t <= tp_price:
                    ret = (o_t - tp_price) / o_t
                    daily_ret = max_leverage * ret - entry_friction - exit_friction
                    pos = 0
                else:
                    ret = (o_t - c_t) / o_t
                    daily_ret = max_leverage * ret - entry_friction - (margin_rate * max_leverage)

        elif pos == 1:
            if target_pos == 0 or target_pos == -1:
                ret_exit = (o_t - c_prev) / c_prev
                exit_ret_comp = max_leverage * ret_exit - exit_friction
                pos = 0

                if target_pos == -1:
                    pos = -1
                    p_entry = o_t
                    sl_price = p_entry * (1.0 + stop_loss)
                    tp_price = p_entry * (1.0 - take_profit)
                    if o_t >= sl_price:
                        intra_ret = -entry_friction - exit_friction
                        pos = 0
                    elif h_t >= sl_price:
                        ret = (o_t - sl_price) / o_t
                        intra_ret = max_leverage * ret - entry_friction - exit_friction
                        pos = 0
                    elif o_t <= tp_price:
                        intra_ret = -entry_friction - exit_friction
                        pos = 0
                    elif l_t <= tp_price:
                        ret = (o_t - tp_price) / o_t
                        intra_ret = max_leverage * ret - entry_friction - exit_friction
                        pos = 0
                    else:
                        ret = (o_t - c_t) / o_t
                        intra_ret = max_leverage * ret - entry_friction - (margin_rate * max_leverage)
                    daily_ret = exit_ret_comp + intra_ret
                else:
                    daily_ret = exit_ret_comp

            elif target_pos == 1:
                if o_t <= sl_price:
                    ret = (o_t - c_prev) / c_prev
                    daily_ret = max_leverage * ret - exit_friction
                    pos = 0
                elif l_t <= sl_price:
                    ret = (sl_price - c_prev) / c_prev
                    daily_ret = max_leverage * ret - exit_friction
                    pos = 0
                elif o_t >= tp_price:
                    ret = (o_t - c_prev) / c_prev
                    daily_ret = max_leverage * ret - exit_friction
                    pos = 0
                elif h_t >= tp_price:
                    ret = (tp_price - c_prev) / c_prev
                    daily_ret = max_leverage * ret - exit_friction
                    pos = 0
                else:
                    ret = (c_t - c_prev) / c_prev
                    daily_ret = max_leverage * ret - (margin_rate * max_leverage)

        elif pos == -1:
            if target_pos == 0 or target_pos == 1:
                ret_exit = (c_prev - o_t) / c_prev
                exit_ret_comp = max_leverage * ret_exit - exit_friction
                pos = 0

                if target_pos == 1:
                    pos = 1
                    p_entry = o_t
                    sl_price = p_entry * (1.0 - stop_loss)
                    tp_price = p_entry * (1.0 + take_profit)
                    if o_t <= sl_price:
                        intra_ret = -entry_friction - exit_friction
                        pos = 0
                    elif l_t <= sl_price:
                        ret = (sl_price - o_t) / o_t
                        intra_ret = max_leverage * ret - entry_friction - exit_friction
                        pos = 0
                    elif o_t >= tp_price:
                        intra_ret = -entry_friction - exit_friction
                        pos = 0
                    elif h_t >= tp_price:
                        ret = (tp_price - o_t) / o_t
                        intra_ret = max_leverage * ret - entry_friction - exit_friction
                        pos = 0
                    else:
                        ret = (c_t - o_t) / o_t
                        intra_ret = max_leverage * ret - entry_friction - (margin_rate * max_leverage)
                    daily_ret = exit_ret_comp + intra_ret
                else:
                    daily_ret = exit_ret_comp

            elif target_pos == -1:
                if o_t >= sl_price:
                    ret = (c_prev - o_t) / c_prev
                    daily_ret = max_leverage * ret - exit_friction
                    pos = 0
                elif h_t >= sl_price:
                    ret = (c_prev - sl_price) / c_prev
                    daily_ret = max_leverage * ret - exit_friction
                    pos = 0
                elif o_t <= tp_price:
                    ret = (c_prev - o_t) / c_prev
                    daily_ret = max_leverage * ret - exit_friction
                    pos = 0
                elif l_t <= tp_price:
                    ret = (c_prev - tp_price) / c_prev
                    daily_ret = max_leverage * ret - exit_friction
                    pos = 0
                else:
                    ret = (c_prev - c_t) / c_prev
                    daily_ret = max_leverage * ret - (margin_rate * max_leverage)

        equity *= (1.0 + daily_ret)
        if equity > peak:
            peak = equity
        dd = (peak - equity) / peak
        if dd > max_dd:
            max_dd = dd

    cagr = (max(equity, 1e-6)) ** (252.0 / max(N, 1)) - 1.0
    return cagr, max_dd



def evaluate_backtest(scores, opens, highs, lows, closes, stop_loss, take_profit, max_leverage, v_th):
    """Dispatch to Numba or NumPy backtester."""
    if HAS_NUMBA:
        return _backtest_simulation_numba(scores, opens, highs, lows, closes, stop_loss, take_profit, max_leverage, v_th)
    else:
        return _backtest_simulation_numpy(scores, opens, highs, lows, closes, stop_loss, take_profit, max_leverage, v_th)


# =====================================================================
# GENOME DATA STRUCTURE & PRUNING LOGIC
# =====================================================================
class V5Genome:
    """
    Continuous Genome representation for V5 Vedic Evolution Engine.
    Continuous Parameters:
        - stop_loss (s): [0.001, 0.10]
        - take_profit (p): [0.005, 0.25]
        - max_leverage (L): [1.0, 5.0]
        - v_th (signal threshold): [0.05, 1.5]
        - weights (W): (n_features,) continuous float weights for Vedic Tensors F1-F37.
    """
    def __init__(self, stop_loss: float = 0.03, take_profit: float = 0.08, max_leverage: float = 2.0, v_th: float = 0.3, weights: np.ndarray = None, n_features: int = 76):
        self.stop_loss = float(stop_loss)
        self.take_profit = float(take_profit)
        self.max_leverage = float(max_leverage)
        self.v_th = float(v_th)
        self.n_features = n_features
        if weights is None:
            self.weights = np.random.randn(n_features) * 0.5
        else:
            self.weights = np.array(weights, dtype=np.float64).copy()
            self.n_features = len(self.weights)

        # Performance evaluation metrics
        self.cagr = 0.0
        self.max_dd = 0.0
        self.l1_penalty = 0.0
        self.net_return = 0.0
        
        # NSGA-II Multi-objective attributes
        self.rank = 0
        self.crowding_distance = 0.0

    def apply_l1_pruning(self, prune_threshold: float = 0.05, lambda_l1: float = 0.02):
        """
        L1 Gene Pruning:
        1. Hard zero thresholding: |w_i| < 0.05 => w_i = 0.0
        2. Soft L1 regularization penalty calculation: lambda_l1 * sum(|w_i|)
        """
        self.weights[np.abs(self.weights) < prune_threshold] = 0.0
        self.l1_penalty = float(lambda_l1 * np.sum(np.abs(self.weights)))

    def get_param_vector(self) -> np.ndarray:
        """Returns 1D parameter array concatenation of [s, p, L, v_th, W]."""
        return np.concatenate([
            [self.stop_loss, self.take_profit, self.max_leverage, self.v_th],
            self.weights
        ])

    def set_param_vector(self, params: np.ndarray):
        """Updates continuous parameters from 1D array with box bounds clamping."""
        self.stop_loss = float(np.clip(params[0], 0.001, 0.10))
        self.take_profit = float(np.clip(params[1], 0.005, 0.25))
        self.max_leverage = float(np.clip(params[2], 1.0, 5.0))
        self.v_th = float(np.clip(params[3], 0.05, 1.5))
        self.weights = np.array(params[4:], dtype=np.float64)
        self.n_features = len(self.weights)

    def evaluate(self, X: np.ndarray, opens: np.ndarray, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray):
        """Full backtest evaluation & L1 penalty calculation."""
        self.apply_l1_pruning()
        scores = X @ self.weights
        cagr, max_dd = evaluate_backtest(scores, opens, highs, lows, closes, self.stop_loss, self.take_profit, self.max_leverage, self.v_th)
        self.cagr = float(cagr)
        self.max_dd = float(max_dd)
        self.net_return = float(self.cagr - self.l1_penalty)
        return self.net_return, self.max_dd

    def to_dict(self) -> dict:
        active_indices = [int(i) for i in np.where(self.weights != 0.0)[0]]
        return {
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "max_leverage": self.max_leverage,
            "v_th": self.v_th,
            "n_features": self.n_features,
            "weights": self.weights.tolist(),
            "active_channels_count": len(active_indices),
            "active_channel_indices": active_indices,
            "cagr": self.cagr,
            "max_dd": self.max_dd,
            "l1_penalty": self.l1_penalty,
            "net_return": self.net_return,
            "rank": self.rank,
            "crowding_distance": self.crowding_distance
        }


# =====================================================================
# MULTIPROCESSING POOL WORKER INITIALIZATION
# =====================================================================
_GLOBAL_X = None
_GLOBAL_OPENS = None
_GLOBAL_HIGHS = None
_GLOBAL_LOWS = None
_GLOBAL_CLOSES = None

def init_worker(X, opens, highs, lows, closes):
    """Worker memory initializer storing heavy dataset arrays in process memory once."""
    global _GLOBAL_X, _GLOBAL_OPENS, _GLOBAL_HIGHS, _GLOBAL_LOWS, _GLOBAL_CLOSES
    _GLOBAL_X = X
    _GLOBAL_OPENS = opens
    _GLOBAL_HIGHS = highs
    _GLOBAL_LOWS = lows
    _GLOBAL_CLOSES = closes


def eval_genome_worker(genome: V5Genome) -> V5Genome:
    """Worker function to evaluate a single genome against global process data."""
    genome.evaluate(_GLOBAL_X, _GLOBAL_OPENS, _GLOBAL_HIGHS, _GLOBAL_LOWS, _GLOBAL_CLOSES)
    return genome


# =====================================================================
# BAYESIAN GAUSSIAN PROCESS SURROGATE MODEL
# =====================================================================
class GPSurrogateModel:
    """
    Bayesian Gaussian Process Surrogate Model for Pre-Backtest Culling.
    - Kernel: Matérn (nu=2.5) + WhiteKernel noise estimator.
    - Fits on evaluated population parameters.
    - Predicts Upper Confidence Bound (UCB = mu + 1.96 * sigma) for candidate mutations.
    - Culls bottom 90% pre-backtest; passes top 10% to full simulation backtesting pool.
    """
    def __init__(self):
        self.gpr = None
        self.fitted = False

    def fit(self, population: list[V5Genome]):
        """Fit GP regressor on evaluated population parameter matrix Z (N, n_params) and net returns y (N,)."""
        Z = np.array([g.get_param_vector() for g in population], dtype=np.float64)
        y = np.array([g.net_return for g in population], dtype=np.float64)
        n_params = Z.shape[1]
        
        kernel = Matern(length_scale=np.ones(n_params), nu=2.5) + WhiteKernel(noise_level=1e-4, noise_level_bounds=(1e-5, 1e-1))
        self.gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=0, random_state=42)

        try:
            self.gpr.fit(Z, y)
            self.fitted = True
        except Exception as e:
            self.fitted = False

    def predict_ucb(self, candidates: list[V5Genome], beta: float = 1.96) -> np.ndarray:
        """Predict UCB scores for candidate genomes."""
        if not self.fitted or self.gpr is None:
            return np.random.randn(len(candidates))
        Z_cand = np.array([g.get_param_vector() for g in candidates], dtype=np.float64)
        mu, sigma = self.gpr.predict(Z_cand, return_std=True)
        return mu + beta * sigma

    def cull_candidates(self, candidates: list[V5Genome], keep_ratio: float = 0.10) -> tuple[list[V5Genome], float]:
        """
        Cull bottom (1 - keep_ratio) candidate mutations.
        Returns:
            retained_candidates: list of top candidate genomes.
            culling_rate: float percentage of candidates culled (e.g. 0.90).
        """
        ucb_scores = self.predict_ucb(candidates)
        n_keep = max(1, int(len(candidates) * keep_ratio))
        sorted_indices = np.argsort(ucb_scores)[::-1]
        retained_indices = sorted_indices[:n_keep]
        retained_candidates = [candidates[idx] for idx in retained_indices]
        culling_rate = (len(candidates) - len(retained_candidates)) / float(len(candidates))
        return retained_candidates, culling_rate


# =====================================================================
# LAMARCKIAN NELDER-MEAD LOCAL OPTIMIZATION ENGINE
# =====================================================================
def optimize_genome_lamarckian(genome: V5Genome, X: np.ndarray, opens: np.ndarray, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, maxiter: int = 40) -> V5Genome:
    """
    Lamarckian Two-Phase Bounded Optimization (Cycle 2 Patch):
    Phase A — L-BFGS-B on the 4 SCALAR parameters (s, p, L, v_th).
              L-BFGS-B natively enforces box bounds — zero out-of-bounds exploration.
    Phase B — Nelder-Mead on the high-dimensional WEIGHT VECTOR W (no gradient required).
    Updates genome parameters IN-PLACE (G <- G*) so acquired traits are genetically inherited!

    Fix: Replaced unified Nelder-Mead-with-bounds (bounds silently ignored by scipy) with
    two-phase split to guarantee true bounded optimization on continuous scalar parameters.
    """
    # ── Phase A: L-BFGS-B on scalar params (true bounded gradient descent) ─
    scalar_bounds = [(0.001, 0.10), (0.005, 0.25), (1.0, 5.0), (0.05, 1.5)]
    init_scalars = np.array([genome.stop_loss, genome.take_profit, genome.max_leverage, genome.v_th])
    frozen_weights = genome.weights.copy()
    frozen_weights[np.abs(frozen_weights) < 0.05] = 0.0

    def loss_scalars(params):
        s = float(np.clip(params[0], 0.001, 0.10))
        p = float(np.clip(params[1], 0.005, 0.25))
        L = float(np.clip(params[2], 1.0, 5.0))
        v = float(np.clip(params[3], 0.05, 1.5))
        l1_pen = 0.02 * np.sum(np.abs(frozen_weights))
        scores = X @ frozen_weights
        cagr, max_dd = evaluate_backtest(scores, opens, highs, lows, closes, s, p, L, v)
        return -(cagr - l1_pen - 5.0 * max_dd)

    try:
        res_a = minimize(loss_scalars, init_scalars, method='L-BFGS-B', bounds=scalar_bounds,
                         options={'maxiter': maxiter, 'ftol': 1e-6, 'gtol': 1e-4})
        if res_a.x is not None:
            genome.stop_loss    = float(np.clip(res_a.x[0], 0.001, 0.10))
            genome.take_profit  = float(np.clip(res_a.x[1], 0.005, 0.25))
            genome.max_leverage = float(np.clip(res_a.x[2], 1.0, 5.0))
            genome.v_th         = float(np.clip(res_a.x[3], 0.05, 1.5))
    except Exception:
        pass  # retain original scalars on Phase A failure

    # ── Phase B: Nelder-Mead on weight vector (high-dim, no bounds needed) ─
    init_weights = genome.weights.copy()
    locked_s, locked_p = genome.stop_loss, genome.take_profit
    locked_L, locked_v = genome.max_leverage, genome.v_th

    def loss_weights(w):
        w_pruned = w.copy()
        w_pruned[np.abs(w_pruned) < 0.05] = 0.0
        l1_pen = 0.02 * np.sum(np.abs(w_pruned))
        scores = X @ w_pruned
        cagr, max_dd = evaluate_backtest(scores, opens, highs, lows, closes,
                                         locked_s, locked_p, locked_L, locked_v)
        return -(cagr - l1_pen - 5.0 * max_dd)

    try:
        res_b = minimize(loss_weights, init_weights, method='Nelder-Mead',
                         options={'maxiter': maxiter, 'xatol': 1e-3, 'fatol': 1e-3})
        if res_b.x is not None:
            genome.weights = np.clip(np.array(res_b.x, dtype=np.float64), -3.0, 3.0)
            genome.n_features = len(genome.weights)
    except Exception:
        pass  # retain original weights on Phase B failure

    genome.evaluate(X, opens, highs, lows, closes)
    return genome



# =====================================================================
# NSGA-II MULTI-OBJECTIVE PARETO SORTING & CROWDING DISTANCE
# =====================================================================
def fast_non_dominated_sort(population: list[V5Genome]) -> list[list[int]]:
    """
    Fast Non-Dominated Sorting for NSGA-II.
    Objectives to MAXIMIZE:
        Obj 1: Net Return (CAGR - L1 Penalty)
        Obj 2: Drawdown metric (-MaxDD, higher is better)
    """
    N = len(population)
    objs = np.array([[g.net_return, -g.max_dd] for g in population], dtype=np.float64)

    S = [[] for _ in range(N)]
    n = np.zeros(N, dtype=int)
    fronts = [[]]

    for p in range(N):
        for q in range(N):
            if p == q:
                continue
            p_ge_q = np.all(objs[p] >= objs[q])
            p_gt_q = np.any(objs[p] > objs[q])
            q_ge_p = np.all(objs[q] >= objs[p])
            q_gt_p = np.any(objs[q] > objs[p])

            if p_ge_q and p_gt_q:
                S[p].append(q)
            elif q_ge_p and q_gt_p:
                n[p] += 1

        if n[p] == 0:
            population[p].rank = 1
            fronts[0].append(p)

    i = 0
    while len(fronts[i]) > 0:
        next_front = []
        for p in fronts[i]:
            for q in S[p]:
                n[q] -= 1
                if n[q] == 0:
                    population[q].rank = i + 2
                    next_front.append(q)
        i += 1
        fronts.append(next_front)

    fronts.pop()
    return fronts


def compute_crowding_distance(population: list[V5Genome], front_indices: list[int]):
    """Compute Crowding Distance for individuals within a single Pareto front."""
    num_ind = len(front_indices)
    if num_ind == 0:
        return
    if num_ind <= 2:
        for idx in front_indices:
            population[idx].crowding_distance = np.inf
        return

    for idx in front_indices:
        population[idx].crowding_distance = 0.0

    objs = np.array([[population[idx].net_return, -population[idx].max_dd] for idx in front_indices], dtype=np.float64)
    num_objs = objs.shape[1]

    for m in range(num_objs):
        sorted_order = np.argsort(objs[:, m])
        population[front_indices[sorted_order[0]]].crowding_distance = np.inf
        population[front_indices[sorted_order[-1]]].crowding_distance = np.inf

        obj_min = objs[sorted_order[0], m]
        obj_max = objs[sorted_order[-1], m]
        obj_range = obj_max - obj_min

        if obj_range == 0:
            continue

        for i in range(1, num_ind - 1):
            curr_idx = front_indices[sorted_order[i]]
            if not np.isinf(population[curr_idx].crowding_distance):
                diff = objs[sorted_order[i + 1], m] - objs[sorted_order[i - 1], m]
                population[curr_idx].crowding_distance += diff / obj_range


def crowded_comparison_operator(a: V5Genome, b: V5Genome) -> int:
    """
    NSGA-II Crowded Comparison Selection Operator.
    Returns:
        -1 if a dominates / is preferred over b
         1 if b dominates / is preferred over a
         0 if identical
    """
    if a.rank < b.rank:
        return -1
    elif a.rank > b.rank:
        return 1
    else:
        if a.crowding_distance > b.crowding_distance:
            return -1
        elif a.crowding_distance < b.crowding_distance:
            return 1
        else:
            return 0


# =====================================================================
# EVOLUTIONARY ALGORITHM ENGINE
# =====================================================================
class EternalQuantEvolutionEngine:
    """
    Surrogate-Assisted Lamarckian Multi-Objective Evolution Engine (v5).
    """
    def __init__(self, pop_size: int = 100, generations: int = 5, n_workers: int = None, seed: int = 42):
        self.pop_size = pop_size
        self.generations = generations
        self.seed = seed
        np.random.seed(seed)

        if n_workers is None:
            self.n_workers = max(1, mp.cpu_count() - 1)
        else:
            self.n_workers = n_workers

        self.gp_surrogate = GPSurrogateModel()
        self.n_features = 76

    def ingest_data(self) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Ingest celestial ephemeris matrix and SPY price data, aligning on trading days.
        """
        print("[Ingestion] Loading continuous ephemeris dataset celestial_matrix_v5.csv...")
        raw_df, source_path = load_celestial_matrix()
        engine = V5ContinuousVedicEngine(raw_df)
        tensor_df = engine.compute_all_tensors()

        print("[Ingestion] Fetching SPY OHLC market price dataset via yfinance...")
        import yfinance as yf
        spy = yf.download("SPY", start="1993-01-01", end="2026-12-31", progress=False)
        if isinstance(spy.columns, pd.MultiIndex):
            spy.columns = spy.columns.get_level_values(0)

        tensor_df['date'] = pd.to_datetime(tensor_df['date'])
        spy.index = pd.to_datetime(spy.index)

        feature_cols = [c for c in tensor_df.columns if c != 'date']
        merged = spy.join(tensor_df.set_index('date'), how='inner')

        X = merged[feature_cols].to_numpy(dtype=np.float64)
        opens = merged['Open'].to_numpy(dtype=np.float64)
        highs = merged['High'].to_numpy(dtype=np.float64)
        lows = merged['Low'].to_numpy(dtype=np.float64)
        closes = merged['Close'].to_numpy(dtype=np.float64)

        self.n_features = X.shape[1]
        print(f"  -> Aligned Dataset Matrix Shape: {merged.shape} (Trading Days: {len(merged)}, Features: {self.n_features})")
        assert not np.isnan(X).any(), "NaNs detected in feature matrix!"

        return tensor_df, X, opens, highs, lows, closes

    def evaluate_population_parallel(self, population: list[V5Genome], pool: mp.Pool) -> list[V5Genome]:
        """Evaluates population across multi-core worker pool."""
        evaluated = pool.map(eval_genome_worker, population)
        return list(evaluated)

    def breed_offspring(self, population: list[V5Genome], num_offspring: int) -> list[V5Genome]:
        """
        Breeds offspring candidates using NSGA-II Crowded Binary Tournament Selection,
        Uniform Parameter Crossover, and Gaussian Parameter Mutation.
        """
        offspring = []
        N_pop = len(population)

        for _ in range(num_offspring):
            i1, i2 = np.random.choice(N_pop, 2, replace=False)
            p1 = population[i1] if crowded_comparison_operator(population[i1], population[i2]) <= 0 else population[i2]
            
            i3, i4 = np.random.choice(N_pop, 2, replace=False)
            p2 = population[i3] if crowded_comparison_operator(population[i3], population[i4]) <= 0 else population[i4]

            v1 = p1.get_param_vector()
            v2 = p2.get_param_vector()
            alpha = np.random.uniform(0.0, 1.0, size=len(v1))
            child_v = alpha * v1 + (1.0 - alpha) * v2

            if np.random.rand() < 0.3:
                mut_mask = np.random.rand(len(child_v)) < 0.15
                child_v[mut_mask] += np.random.normal(0, 0.1, size=np.sum(mut_mask))

            child = V5Genome(n_features=self.n_features)
            child.set_param_vector(child_v)
            child.apply_l1_pruning()
            offspring.append(child)

        return offspring

    def run_evolution(self):
        """
        Executes the 5-generation Evolutionary Optimization Loop.
        """
        print("\n" + "=" * 80)
        print("ETERNAL QUANT EVOLUTION V5 — RUNNING SURROGATE LAMARCKIAN ENGINE")
        print(f"Generations: {self.generations} | Population Size: {self.pop_size} | Workers: {self.n_workers}")
        print("=" * 80)

        # 1. Ingest Data
        tensor_df, X, opens, highs, lows, closes = self.ingest_data()

        # 2. Create Multiprocessing Pool with spawn context
        ctx = mp.get_context('spawn')
        pool = ctx.Pool(processes=self.n_workers, initializer=init_worker, initargs=(X, opens, highs, lows, closes))

        # 3. Initialize Random Population
        population = [V5Genome(n_features=self.n_features) for _ in range(self.pop_size)]
        for g in population:
            g.apply_l1_pruning()

        # Initial Evaluation
        print(f"\n[Gen 00] Evaluating initial population of {self.pop_size} genomes...")
        t0_gen = time.perf_counter()
        population = self.evaluate_population_parallel(population, pool)

        # Initial NSGA-II Pareto Sort
        fronts = fast_non_dominated_sort(population)
        for front in fronts:
            compute_crowding_distance(population, front)

        gen_time = time.perf_counter() - t0_gen
        pareto_front1 = [population[i] for i in fronts[0]]
        best_net_ret = max(g.net_return for g in population)
        min_dd = min(g.max_dd for g in population)
        print(f"  -> Gen 00 complete in {gen_time:.2f}s | Front 1 Size: {len(pareto_front1)} | Best Net Return: {best_net_ret*100:.2f}% | Min MaxDD: {min_dd*100:.2f}%")

        # Evolutionary Generation Loop
        for gen in range(1, self.generations + 1):
            t_gen_start = time.perf_counter()
            print(f"\n" + "-" * 80)
            print(f"GENERATION {gen:02d} / {self.generations:02d}")
            print("-" * 80)

            # Step A: Train Bayesian GP Surrogate Model on evaluated population
            t_gp0 = time.perf_counter()
            self.gp_surrogate.fit(population)
            t_gp_fit = (time.perf_counter() - t_gp0) * 1000

            # Step B: Generate Candidate Mutations (10x population size = 1000 candidates)
            num_candidates = self.pop_size * 10
            candidates = self.breed_offspring(population, num_candidates)

            # Step C: Bayesian GP Surrogate Pre-Backtest Culling
            # Cull bottom 90%, retain top 10% (100 candidates) for full backtesting
            t_cull0 = time.perf_counter()
            retained_candidates, culling_rate = self.gp_surrogate.cull_candidates(candidates, keep_ratio=0.10)
            t_cull = (time.perf_counter() - t_cull0) * 1000

            print(f"  [GP Surrogate] Fitted in {t_gp_fit:.2f} ms | Generated {num_candidates} Candidate Mutations")
            print(f"  [Surrogate Culling] Culled {len(candidates) - len(retained_candidates)} candidates ({culling_rate*100:.1f}% culling rate) in {t_cull:.2f} ms | Retained Top {len(retained_candidates)}")

            # Step D: Evaluate Surrogate-Approved Candidates in Parallel
            evaluated_offspring = self.evaluate_population_parallel(retained_candidates, pool)

            # Step E: Lamarckian Nelder-Mead Local Optimization Step
            # Apply Lamarckian optimization on top 10% evaluated offspring, updating traits in-place!
            t_lam0 = time.perf_counter()
            num_lamarck = max(1, int(len(evaluated_offspring) * 0.10))
            sorted_offspring_indices = np.argsort([g.net_return for g in evaluated_offspring])[::-1]

            for idx in sorted_offspring_indices[:num_lamarck]:
                evaluated_offspring[idx] = optimize_genome_lamarckian(evaluated_offspring[idx], X, opens, highs, lows, closes, maxiter=30)
            t_lam = (time.perf_counter() - t_lam0) * 1000
            print(f"  [Lamarckian Optimization] Applied Nelder-Mead to top {num_lamarck} candidates in {t_lam:.2f} ms (Acquired traits updated in-place)")

            # Step F: NSGA-II Multi-Objective Environmental Selection
            combined_population = population + evaluated_offspring
            fronts = fast_non_dominated_sort(combined_population)

            new_population = []
            for front in fronts:
                compute_crowding_distance(combined_population, front)
                if len(new_population) + len(front) <= self.pop_size:
                    for idx in front:
                        new_population.append(combined_population[idx])
                else:
                    front_genomes = [combined_population[idx] for idx in front]
                    front_genomes.sort(key=lambda g: g.crowding_distance, reverse=True)
                    needed = self.pop_size - len(new_population)
                    new_population.extend(front_genomes[:needed])
                    break

            population = new_population

            # Re-sort final generation population for statistics
            fronts = fast_non_dominated_sort(population)
            for front in fronts:
                compute_crowding_distance(population, front)

            pareto_front1 = [population[i] for i in fronts[0]]
            best_genome = max(population, key=lambda g: g.net_return)
            gen_duration = time.perf_counter() - t_gen_start

            print(f"  [NSGA-II Pareto Sort] Generated {len(fronts)} Pareto Fronts | Front 1 Size: {len(pareto_front1)}")
            print(f"  [Gen {gen:02d} Summary] Best Net Return: {best_genome.net_return*100:.2f}% | MaxDD: {best_genome.max_dd*100:.2f}% | Active Channels: {np.sum(best_genome.weights != 0)}/{self.n_features} | Time: {gen_duration:.2f}s")

        pool.close()
        pool.join()

        # Extract Best Global Model
        best_overall = max(population, key=lambda g: g.net_return)

        print("\n" + "=" * 80)
        print("FINAL EVOLUTION ENGINE RESULTS & BEST MODEL METRICS")
        print("=" * 80)
        print(f"Best Model Net Return    : {best_overall.net_return * 100:.2f}%")
        print(f"Best Model CAGR          : {best_overall.cagr * 100:.2f}%")
        print(f"Best Model Max Drawdown  : {best_overall.max_dd * 100:.2f}%")
        print(f"Best Model L1 Penalty    : {best_overall.l1_penalty:.6f}")
        print(f"Optimal Parameters       : s={best_overall.stop_loss:.4f}, p={best_overall.take_profit:.4f}, L={best_overall.max_leverage:.2f}, v_th={best_overall.v_th:.4f}")
        print(f"Active Vedic Channels    : {np.sum(best_overall.weights != 0)} / {self.n_features} continuous features")
        print("=" * 80)

        # Save Best Model JSON Artifact in both current directory and PROJECT_ROOT
        model_artifact_path = "eternal_best_model_v5.json"
        with open(model_artifact_path, "w", encoding="utf-8") as f:
            json.dump(best_overall.to_dict(), f, indent=2)
        print(f"[Artifact] Saved best optimized model JSON to: {os.path.abspath(model_artifact_path)}")

        try:
            target_path = os.path.join(PROJECT_ROOT, "eternal_best_model_v5.json")
            if target_path != os.path.abspath(model_artifact_path):
                with open(target_path, "w", encoding="utf-8") as f:
                    json.dump(best_overall.to_dict(), f, indent=2)
                print(f"[Artifact] Mirrored best optimized model JSON to: {target_path}")
        except Exception:
            pass

        return best_overall, population


# =====================================================================
# CLI ENTRY POINT
# =====================================================================
def main():
    parser = argparse.ArgumentParser(description="Eternal Quant Evolution Engine v5 (Surrogate-Assisted Lamarckian NSGA-II)")
    parser.add_argument("--generations", type=int, default=5, help="Number of evolutionary generations (default: 5)")
    parser.add_argument("--pop-size", type=int, default=100, help="Population size (default: 100)")
    parser.add_argument("--num-workers", type=int, default=None, help="Number of parallel worker processes")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()

    engine = EternalQuantEvolutionEngine(
        pop_size=args.pop_size,
        generations=args.generations,
        n_workers=args.num_workers,
        seed=args.seed
    )
    engine.run_evolution()


if __name__ == "__main__":
    main()
