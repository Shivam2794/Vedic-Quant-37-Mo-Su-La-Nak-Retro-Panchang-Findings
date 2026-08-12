import numpy as np
import pandas as pd
from scipy.optimize import minimize
import numba

def compute_pairwise_covariance(ret_block):
    """
    Computes covariance matrix ignoring NaNs pairwise.
    ret_block: (N_assets, T) array of returns.
    """
    N = ret_block.shape[0]
    cov = np.zeros((N, N))
    for i in range(N):
        for j in range(i, N):
            mask = ~np.isnan(ret_block[i]) & ~np.isnan(ret_block[j])
            if mask.sum() > 2:
                c = np.cov(ret_block[i][mask], ret_block[j][mask])[0, 1]
            else:
                c = 0.0 # Not enough data
            cov[i, j] = c
            cov[j, i] = c
    return cov

def risk_budget_objective(weights, cov):
    """
    Objective function for Equal Risk Contribution (ERC).
    Minimize sum of squared differences between risk contributions.
    """
    weights = np.array(weights)
    port_var = weights.T @ cov @ weights
    if port_var <= 0:
        return 1e9
    
    port_vol = np.sqrt(port_var)
    marginal_contrib = cov @ weights
    risk_contrib = weights * marginal_contrib
    
    # Target risk contribution is equal for all active assets
    # Active assets are those where weight can be non-zero
    target_risk = port_var / len(weights)
    
    # We want to minimize the squared error from the target
    # Scale error by 1e12 to prevent premature convergence due to small float values
    error = np.sum((risk_contrib - target_risk)**2) * 1e12
    return error

def get_erc_weights_for_date(cov, active_mask):
    """
    Calculate ERC weights for a single date given the covariance matrix and which assets are active.
    active_mask: boolean array of size N indicating which assets to include.
    """
    N = len(cov)
    weights = np.zeros(N)
    
    n_active = np.sum(active_mask)
    if n_active == 0:
        return weights
    if n_active == 1:
        weights[active_mask] = 1.0
        return weights
        
    active_cov = cov[np.ix_(active_mask, active_mask)]
    
    # Check if active_cov has zeros on diagonal
    if np.any(np.diag(active_cov) <= 0):
        # Fallback to equal weight if invalid cov
        weights[active_mask] = 1.0 / n_active
        return weights
        
    init_guess = np.ones(n_active) / n_active
    bounds = [(0.0, 1.0) for _ in range(n_active)]
    constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0})
    
    res = minimize(
        risk_budget_objective, 
        init_guess, 
        args=(active_cov,), 
        method='SLSQP',
        bounds=bounds, 
        constraints=constraints,
        options={'disp': False, 'ftol': 1e-7}
    )
    
    if res.success:
        weights[active_mask] = res.x
    else:
        weights[active_mask] = 1.0 / n_active
        
    return weights

def calculate_dynamic_erc_weights(returns, positions, lookback=252):
    """
    returns: (N_assets, T) array
    positions: (N_assets, T) array of 1/0 indicating if we WANT to hold it.
    Returns:
    weights: (N_assets, T) array of ERC weights.
    """
    N, T = returns.shape
    weights = np.zeros((N, T))
    
    for t in range(lookback, T):
        active_assets = positions[:, t] > 0
        if not np.any(active_assets):
            continue
            
        ret_block = returns[:, t-lookback:t]
        cov = compute_pairwise_covariance(ret_block)
        
        w = get_erc_weights_for_date(cov, active_assets)
        weights[:, t] = w
        
    return weights
