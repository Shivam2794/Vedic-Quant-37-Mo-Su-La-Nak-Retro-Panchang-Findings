import numpy as np

def erc_ccd(S, b=None, iters=200, tol=1e-12):
    """Exact ERC via cyclical coordinate descent on the log-barrier form.
       Griveau-Billion/Richard/Roncalli (2013). S must be PSD, diag>0."""
    k = S.shape[0]
    if k == 0:
        return np.array([])
    if k == 1:
        return np.array([1.0])
        
    b = np.full(k, 1.0/k) if b is None else b/np.sum(b)
    
    # Safe diagonal extraction
    d = np.diag(S)
    if np.any(d <= 0):
        # Fallback to inverse vol if PSD violation or zero variance
        d = np.clip(d, 1e-12, None)
        w = 1.0 / np.sqrt(d)
        return w / w.sum()
        
    d = np.sqrt(d)
    w = (b/d)
    w /= w.sum() # inverse-vol warm start (exact for k=2)
    
    for _ in range(iters):
        w_old = w.copy()
        for i in range(k):
            a  = S[i, i]
            bb = S[i] @ w - a*w[i]               # Σ_{j≠i} S_ij w_j
            w[i] = (-bb + np.sqrt(bb*bb + 4.0*a*b[i])) / (2.0*a)
        if np.max(np.abs(w - w_old)) < tol:
            break
            
    return w / w.sum()

def pool_cov(ret_block_sub):
    """
    Computes complete-case covariance for a specific pool of assets.
    ret_block_sub: (k, L) array of returns for the k assets over L days.
    """
    ok = np.isfinite(ret_block_sub).all(axis=0)  # complete cases
    
    # Require at least 20 observations or 5*k, whichever is larger
    min_obs = max(20, 5 * ret_block_sub.shape[0])
    
    if ok.sum() < min_obs:
        return None  # refuse to trade, don't guess
        
    X = ret_block_sub[:, ok]
    S = np.cov(X, ddof=1)
    
    # psd_repair + shrink
    eps = 1e-12
    delta = 0.10
    
    # Symmetrize
    S = 0.5 * (S + S.T)
    
    # Eigendecomposition to fix non-PSD
    eigval, eigvec = np.linalg.eigh(S)
    eigval = np.clip(eigval, eps, None)
    S = eigvec @ np.diag(eigval) @ eigvec.T
    
    # Ledoit-Wolf-lite shrinkage toward diagonal
    D = np.diag(np.diag(S))
    S = (1 - delta) * S + delta * D
    
    return S

def calculate_dynamic_erc_weights(returns_matrix, pool_indices, lookback=60):
    """
    Computes ERC weights daily for a FIXED pool of assets.
    returns_matrix: (N, T) global returns
    pool_indices: list of indices of the assets in the pool
    """
    N, T = returns_matrix.shape
    k = len(pool_indices)
    
    weights = np.zeros((N, T))
    
    if k == 1:
        idx = pool_indices[0]
        valid = np.isfinite(returns_matrix[idx, :])
        weights[idx, valid] = 1.0
        return weights
        
    # Extract just the sub-matrix for this pool
    sub_returns = returns_matrix[pool_indices, :]
    
    for t in range(lookback, T):
        ret_block = sub_returns[:, t-lookback:t]
        S = pool_cov(ret_block)
        
        if S is not None:
            w = erc_ccd(S)
            for i, idx in enumerate(pool_indices):
                weights[idx, t] = w[i]
                
    return weights
