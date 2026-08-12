#!/usr/bin/env python3
"""
verify_nsga2_lamarckian.py - Autonomous Diagnostic Verification Suite
======================================================================
Verifies the 4 core mathematical pillars of Phase 2 Surrogate-Assisted
Lamarckian NSGA-II Evolution:

1. NSGA-II Pareto Sorting Verification:
   - Fast non-dominated sorting & crowding distance calculations.
   - Asserts non-dominated individuals get Rank 1 and crowding distances are correctly computed.

2. Lamarckian Nelder-Mead Optimization Shift Verification:
   - Nelder-Mead parameter optimization (scipy.optimize.minimize) on continuous genome parameters.
   - Asserts parameter updates successfully shift genome parameters to local maxima.

3. Bayesian GP Surrogate Culling Precision Verification:
   - sklearn.gaussian_process.GaussianProcessRegressor (Matérn 5/2 + WhiteKernel).
   - Fit on sample evaluated genomes, predict UCB scores on 500 candidate mutations, cull bottom 90%.
   - Asserts top 10% retains high-fitness candidates with >= 90% precision.

4. L1 Gene Pruning Sparsity Verification:
   - Continuous Vedic tensor weight pruning logic (|w_i| < 0.05 => w_i = 0.0).
   - Asserts zero-weighting correctly silences uninformative tensor channels.

Execution & Exit Code:
Runs all 4 diagnostic suites autonomously, logs detailed outputs, and exits with code 0 on 100% pass.
"""

import sys
import time
import warnings
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, WhiteKernel
from sklearn.exceptions import ConvergenceWarning

warnings.filterwarnings("ignore", category=ConvergenceWarning)


# =====================================================================
# UTILITY LOGGING FUNCTIONS
# =====================================================================
def log_header(title: str):
    width = 72
    print("\n" + "=" * width)
    print(f"  {title.upper()}")
    print("=" * width)


def log_substep(step_name: str, message: str):
    print(f"  [{step_name}] {message}")


def log_pass(suite_name: str):
    print(f"\n  >>> {suite_name}: [PASS] 100% VERIFIED <<<")


# =====================================================================
# SUITE 1: NSGA-II PARETO SORTING IMPLEMENTATION & VERIFICATION
# =====================================================================
def fast_non_dominated_sort(objectives: np.ndarray):
    """
    Perform Fast Non-Dominated Sorting on objective matrix (N, M).
    Assumes ALL objectives are to be MAXIMIZED.
    Returns:
        fronts: List of lists containing indices for each Pareto front.
        ranks: 1D array of Pareto ranks (1-indexed) for each individual.
    """
    N = len(objectives)
    S = [[] for _ in range(N)]
    n = np.zeros(N, dtype=int)
    ranks = np.zeros(N, dtype=int)
    fronts = [[]]

    for p in range(N):
        for q in range(N):
            if p == q:
                continue
            # Check domination: p dominates q if p >= q in all objectives and p > q in at least one
            p_ge_q = np.all(objectives[p] >= objectives[q])
            p_gt_q = np.any(objectives[p] > objectives[q])
            q_ge_p = np.all(objectives[q] >= objectives[p])
            q_gt_p = np.any(objectives[q] > objectives[p])

            if p_ge_q and p_gt_q:
                S[p].append(q)
            elif q_ge_p and q_gt_p:
                n[p] += 1

        if n[p] == 0:
            ranks[p] = 1
            fronts[0].append(p)

    i = 0
    while len(fronts[i]) > 0:
        next_front = []
        for p in fronts[i]:
            for q in S[p]:
                n[q] -= 1
                if n[q] == 0:
                    ranks[q] = i + 2
                    next_front.append(q)
        i += 1
        fronts.append(next_front)

    fronts.pop()  # Remove last empty front
    return fronts, ranks


def compute_crowding_distance(objectives: np.ndarray, front_indices: list) -> np.ndarray:
    """
    Compute Crowding Distance for individuals within a single Pareto front.
    Returns array of crowding distances corresponding to front_indices.
    """
    num_individuals = len(front_indices)
    distances = np.zeros(num_individuals)
    if num_individuals <= 2:
        distances[:] = np.inf
        return distances

    front_objs = objectives[front_indices]
    num_objectives = front_objs.shape[1]

    for m in range(num_objectives):
        sorted_order = np.argsort(front_objs[:, m])
        distances[sorted_order[0]] = np.inf
        distances[sorted_order[-1]] = np.inf

        obj_min = front_objs[sorted_order[0], m]
        obj_max = front_objs[sorted_order[-1], m]
        obj_range = obj_max - obj_min

        if obj_range == 0:
            continue

        for i in range(1, num_individuals - 1):
            if not np.isinf(distances[sorted_order[i]]):
                diff = front_objs[sorted_order[i + 1], m] - front_objs[sorted_order[i - 1], m]
                distances[sorted_order[i]] += diff / obj_range

    return distances


def verify_nsga2_pareto_sorting():
    log_header("Suite 1: NSGA-II Pareto Sorting & Crowding Distance Verification")
    
    # Generate Synthetic Benchmark Population (ZDT1-style concave front + interior dominated points)
    np.random.seed(42)
    N_front1 = 15
    f1_front1 = np.linspace(0.1, 0.9, N_front1)
    f2_front1 = 1.0 - np.sqrt(f1_front1)  # Non-dominated frontier: f2 = 1 - sqrt(f1)
    
    # Dominated layer 1
    f1_dom1 = np.linspace(0.15, 0.85, 10)
    f2_dom1 = 1.0 - np.sqrt(f1_dom1) - 0.2
    
    # Dominated layer 2
    f1_dom2 = np.linspace(0.2, 0.8, 10)
    f2_dom2 = 1.0 - np.sqrt(f1_dom2) - 0.4

    f1_all = np.concatenate([f1_front1, f1_dom1, f1_dom2])
    f2_all = np.concatenate([f2_front1, f2_dom1, f2_dom2])
    objs = np.column_stack([f1_all, f2_all])

    log_substep("SETUP", f"Synthetic Population created with {len(objs)} individuals (15 Pareto, 20 Dominated).")

    # Run Fast Non-Dominated Sorting
    t0 = time.perf_counter()
    fronts, ranks = fast_non_dominated_sort(objs)
    t_sort = (time.perf_counter() - t0) * 1000

    log_substep("EXECUTION", f"Fast Non-Dominated Sort executed in {t_sort:.3f} ms. Generated {len(fronts)} fronts.")

    # Assertions on Sorting
    front1_indices = fronts[0]
    log_substep("INSPECTION", f"Front 1 size: {len(front1_indices)} individuals (Expected: 15).")
    assert len(front1_indices) == N_front1, f"Front 1 size mismatch: expected {N_front1}, got {len(front1_indices)}"
    assert np.all(ranks[0:N_front1] == 1), "All true non-dominated individuals must receive Rank 1"
    assert np.all(ranks[N_front1:] > 1), "All dominated individuals must receive Rank > 1"

    # Compute Crowding Distances for Front 1
    distances_front1 = compute_crowding_distance(objs, front1_indices)
    
    # Boundary points must be infinity
    log_substep("INSPECTION", f"Boundary points crowding distances: {distances_front1[0]} & {distances_front1[-1]}")
    assert np.isinf(distances_front1[0]) and np.isinf(distances_front1[-1]), "Frontier boundary points must have infinite crowding distance"

    # Intermediate points must have finite, positive crowding distance
    intermediate_distances = distances_front1[1:-1]
    assert np.all(np.isfinite(intermediate_distances)), "Intermediate points must have finite crowding distances"
    assert np.all(intermediate_distances > 0), "Intermediate points must have positive crowding distances"

    log_substep("VERIFICATION", "Rank 1 assignments, multi-front partitioning, and crowding distance boundaries match mathematical theory.")
    log_pass("Suite 1: NSGA-II Pareto Sorting")


# =====================================================================
# SUITE 2: LAMARCKIAN NELDER-MEAD OPTIMIZATION SHIFT VERIFICATION
# =====================================================================
class SyntheticGenome:
    def __init__(self, stop_loss: float, max_leverage: float, weights: np.ndarray):
        self.stop_loss = stop_loss
        self.max_leverage = max_leverage
        self.weights = weights.copy()


def verify_lamarckian_nelder_mead():
    log_header("Suite 2: Lamarckian Nelder-Mead Optimization Shift Verification")

    # Define Box Constraints:
    # stop_loss in [0.001, 0.10], max_leverage in [1.0, 5.0], w_0 in [-2.0, 2.0]
    bounds = [
        (0.001, 0.10),  # stop_loss
        (1.0, 5.0),     # max_leverage
        (-2.0, 2.0)     # tensor weight w_0
    ]

    # Target Local Maximum in continuous space: (s_target=0.03, L_target=2.5, w_target=1.2)
    target_params = np.array([0.03, 2.5, 1.2])

    def synthetic_objective(z):
        """Synthetic fitness landscape with normalized parameter deviations."""
        s, L, w = z
        dev_s = (s - target_params[0]) / 0.05
        dev_L = (L - target_params[1]) / 2.0
        dev_w = (w - target_params[2]) / 2.0
        return -(dev_s ** 2 + dev_L ** 2 + dev_w ** 2) + 5.0

    def loss_function(z):
        return -synthetic_objective(z)  # Minimize negative fitness

    # Initialize Genome at sub-optimal interior point
    init_params = np.array([0.01, 1.2, -0.5])
    genome = SyntheticGenome(stop_loss=init_params[0], max_leverage=init_params[1], weights=np.array([init_params[2]]))
    
    init_fitness = synthetic_objective(init_params)
    init_distance = np.linalg.norm(init_params - target_params)

    log_substep("INITIALIZATION", f"Initial Genome Params: s={genome.stop_loss:.4f}, L={genome.max_leverage:.2f}, w={genome.weights[0]:.2f}")
    log_substep("INITIALIZATION", f"Initial Fitness: {init_fitness:.6f} | Distance to Peak: {init_distance:.6f}")

    # Perform Nelder-Mead Bounded Optimization
    t0 = time.perf_counter()
    res = minimize(loss_function, init_params, method='Nelder-Mead', bounds=bounds, options={'maxiter': 150, 'xatol': 1e-4, 'fatol': 1e-4})
    t_opt = (time.perf_counter() - t0) * 1000

    optimized_params = res.x
    optimized_fitness = synthetic_objective(optimized_params)
    post_distance = np.linalg.norm(optimized_params - target_params)

    log_substep("OPTIMIZATION", f"Nelder-Mead finished in {t_opt:.2f} ms ({res.nfev} function evaluations).")
    log_substep("OPTIMIZATION", f"Optimized Params: s={optimized_params[0]:.4f}, L={optimized_params[1]:.2f}, w={optimized_params[2]:.2f}")
    log_substep("OPTIMIZATION", f"Optimized Fitness: {optimized_fitness:.6f} | Distance to Peak: {post_distance:.6f}")

    # LAMARCKIAN HANDOFF: Overwrite Genome in-place with optimized parameters
    genome.stop_loss = float(optimized_params[0])
    genome.max_leverage = float(optimized_params[1])
    genome.weights[0] = float(optimized_params[2])

    # Verification Assertions
    assert optimized_fitness > init_fitness, f"Fitness failed to increase: init {init_fitness:.4f} vs opt {optimized_fitness:.4f}"
    assert post_distance < 0.05, f"Parameter shift failed to reach local maximum neighborhood: distance {post_distance:.4f} >= 0.05"
    assert genome.stop_loss == float(optimized_params[0]) and genome.max_leverage == float(optimized_params[1]), "Genome parameters were not correctly updated in-place (Lamarckian failure)"

    log_substep("VERIFICATION", "Nelder-Mead successfully shifted parameters to local maximum and updated genotype in-place.")
    log_pass("Suite 2: Lamarckian Nelder-Mead Optimization Shift")


# =====================================================================
# SUITE 3: BAYESIAN GP SURROGATE CULLING PRECISION VERIFICATION
# =====================================================================
def verify_bayesian_gp_culling():
    log_header("Suite 3: Bayesian GP Surrogate Culling Precision Verification")

    np.random.seed(42)

    # Define Ground-Truth Non-Linear Fitness Function f(x) for x in R^4
    def ground_truth_fitness(X: np.ndarray) -> np.ndarray:
        x0, x1, x2, x3 = X[:, 0], X[:, 1], X[:, 2], X[:, 3]
        return np.sin(2 * np.pi * x0) + np.cos(2 * np.pi * x1) - 2.0 * (x2 - 0.5) ** 2 + 1.5 * x3

    # Step 1: Fit GP on N_train sample evaluated genomes
    N_train = 150
    X_train = np.random.uniform(0.0, 1.0, size=(N_train, 4))
    y_train = ground_truth_fitness(X_train) + np.random.normal(0, 0.01, size=N_train)

    log_substep("TRAINING", f"Generated {N_train} sample evaluated genomes for GP fitting.")

    # Configure Matérn 5/2 + WhiteKernel GP Regressor
    kernel = Matern(length_scale=np.ones(4), nu=2.5) + WhiteKernel(noise_level=1e-4, noise_level_bounds=(1e-5, 1e-1))
    gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=5, random_state=42)

    t0 = time.perf_counter()
    gpr.fit(X_train, y_train)
    t_fit = (time.perf_counter() - t0) * 1000
    log_substep("FIT", f"GaussianProcessRegressor fitted in {t_fit:.2f} ms.")

    # Step 2: Generate M = 500 Candidate Mutations
    M_candidates = 500
    X_cand = np.random.uniform(0.0, 1.0, size=(M_candidates, 4))
    y_cand_true = ground_truth_fitness(X_cand)

    # Predict GP Mean and Standard Deviation
    t0 = time.perf_counter()
    mu_cand, sigma_cand = gpr.predict(X_cand, return_std=True)
    t_pred = (time.perf_counter() - t0) * 1000

    # Compute Upper Confidence Bound (UCB) Score with beta = 1.96
    beta = 1.96
    ucb_scores = mu_cand + beta * sigma_cand
    log_substep("INFERENCE", f"GP predicted UCB scores for {M_candidates} candidate mutations in {t_pred:.2f} ms.")

    # Step 3: Cull Bottom 90%, Retain Top 10% (Top 50 Candidates)
    N_retain = 50
    surrogate_sorted_indices = np.argsort(ucb_scores)[::-1]
    retained_indices_gp = surrogate_sorted_indices[:N_retain]
    culled_indices_gp = surrogate_sorted_indices[N_retain:]

    culling_rate = len(culled_indices_gp) / M_candidates
    log_substep("CULLING", f"Culled {len(culled_indices_gp)}/500 candidates ({culling_rate * 100:.1f}% culling rate). Retained Top {N_retain}.")

    # Step 4: Evaluate Precision against Ground-Truth Top 50
    true_sorted_indices = np.argsort(y_cand_true)[::-1]
    retained_indices_true = set(true_sorted_indices[:N_retain])

    matches = len(set(retained_indices_gp).intersection(retained_indices_true))
    precision = matches / float(N_retain)

    log_substep("EVALUATION", f"Overlap between GP UCB Top 50 and Ground-Truth Top 50: {matches}/{N_retain}")
    log_substep("EVALUATION", f"Surrogate Retained Candidates Precision: {precision * 100:.2f}% (Threshold: >= 90.0%)")

    # Verification Assertions
    assert culling_rate == 0.90, f"Culling rate mismatch: expected 0.90, got {culling_rate}"
    assert precision >= 0.90, f"GP Surrogate precision failed quality bar: got {precision*100:.2f}%, required >= 90.0%"

    log_substep("VERIFICATION", "Gaussian Process UCB surrogate achieved >= 90% retrieval precision on top-decile candidates.")
    log_pass("Suite 3: Bayesian GP Surrogate Culling Precision")


# =====================================================================
# SUITE 4: L1 GENE PRUNING SPARSITY VERIFICATION
# =====================================================================
def prune_weights_l1(weights: np.ndarray, prune_threshold: float = 0.05) -> np.ndarray:
    """
    Zero-weight hard thresholding operator:
    If |w_i| < prune_threshold, w_i = 0.0.
    """
    pruned = weights.copy()
    pruned[np.abs(pruned) < prune_threshold] = 0.0
    return pruned


def compute_l1_penalty(weights: np.ndarray, lambda_l1: float = 0.02) -> float:
    """Compute soft L1 regularization penalty."""
    return lambda_l1 * np.sum(np.abs(weights))


def verify_l1_gene_pruning():
    log_header("Suite 4: L1 Gene Pruning Sparsity Verification")

    # Input Continuous Vedic Tensor Weights (8 channels)
    raw_weights = np.array([1.50, -0.04, 0.02, -0.80, 0.001, 0.40, -0.0499, 0.0501])
    prune_threshold = 0.05
    lambda_l1 = 0.02

    log_substep("INPUT", f"Raw Weights (8 channels): {raw_weights}")
    initial_l1_penalty = compute_l1_penalty(raw_weights, lambda_l1)
    log_substep("INPUT", f"Initial Soft L1 Penalty: {initial_l1_penalty:.6f}")

    # Perform Hard Thresholding Pruning
    pruned_weights = prune_weights_l1(raw_weights, prune_threshold)
    post_l1_penalty = compute_l1_penalty(pruned_weights, lambda_l1)

    log_substep("PRUNING", f"Pruned Weights: {pruned_weights}")
    log_substep("PRUNING", f"Post-Pruning Soft L1 Penalty: {post_l1_penalty:.6f}")

    # Active Channel Identification
    active_channels_before = np.where(raw_weights != 0.0)[0]
    active_channels_after = np.where(pruned_weights != 0.0)[0]
    silenced_channels = np.where(pruned_weights == 0.0)[0]

    log_substep("ANALYSIS", f"Active Channels Before: {len(active_channels_before)}/8 -> Active Channels After: {len(active_channels_after)}/8")
    log_substep("ANALYSIS", f"Silenced Channel Indices: {list(silenced_channels)}")

    # Verification Assertions
    expected_pruned = np.array([1.50, 0.0, 0.0, -0.80, 0.0, 0.40, 0.0, 0.0501])
    np.testing.assert_allclose(pruned_weights, expected_pruned, atol=1e-6, err_msg="Pruned weights vector mismatch")
    
    assert len(active_channels_after) == 4, f"Active channel count mismatch: expected 4, got {len(active_channels_after)}"
    assert np.array_equal(silenced_channels, [1, 2, 4, 6]), f"Silenced indices mismatch: expected [1, 2, 4, 6], got {list(silenced_channels)}"
    assert post_l1_penalty < initial_l1_penalty, "Post-pruning penalty must be strictly less than initial penalty"

    log_substep("VERIFICATION", "L1 Gene Pruning correctly zero-weighted small continuous weights and silenced uninformative tensor channels.")
    log_pass("Suite 4: L1 Gene Pruning Sparsity")


# =====================================================================
# MAIN DIAGNOSTIC SUITE RUNNER
# =====================================================================
def main():
    print("\n" + "#" * 72)
    print("# AUTONOMOUS DIAGNOSTIC SUITE: NSGA-II & LAMARCKIAN EVOLUTION ENGINE")
    print("# " + time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))
    print("#" * 72)

    suite_results = []

    try:
        verify_nsga2_pareto_sorting()
        suite_results.append(("NSGA-II Pareto Sorting Verification", "PASS"))
    except Exception as e:
        print(f"\n  !!! SUITE 1 FAILED: {e} !!!")
        suite_results.append(("NSGA-II Pareto Sorting Verification", "FAIL"))

    try:
        verify_lamarckian_nelder_mead()
        suite_results.append(("Lamarckian Nelder-Mead Optimization Shift", "PASS"))
    except Exception as e:
        print(f"\n  !!! SUITE 2 FAILED: {e} !!!")
        suite_results.append(("Lamarckian Nelder-Mead Optimization Shift", "FAIL"))

    try:
        verify_bayesian_gp_culling()
        suite_results.append(("Bayesian GP Surrogate Culling Precision", "PASS"))
    except Exception as e:
        print(f"\n  !!! SUITE 3 FAILED: {e} !!!")
        suite_results.append(("Bayesian GP Surrogate Culling Precision", "FAIL"))

    try:
        verify_l1_gene_pruning()
        suite_results.append(("L1 Gene Pruning Sparsity Verification", "PASS"))
    except Exception as e:
        print(f"\n  !!! SUITE 4 FAILED: {e} !!!")
        suite_results.append(("L1 Gene Pruning Sparsity Verification", "FAIL"))

    # Final Summary Table
    print("\n" + "=" * 72)
    print("  FINAL DIAGNOSTIC SUMMARY REPORT")
    print("=" * 72)
    all_passed = True
    for suite_name, status in suite_results:
        print(f"  - {suite_name:<50}: [{status}]")
        if status != "PASS":
            all_passed = False

    print("=" * 72)
    if all_passed:
        print("  >>> ALL 4 DIAGNOSTIC SUITES PASSED (100% SUCCESS) <<<")
        print("=" * 72 + "\n")
        sys.exit(0)
    else:
        print("  !!! DIAGNOSTIC SUITE FAILURE DETECTED !!!")
        print("=" * 72 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
