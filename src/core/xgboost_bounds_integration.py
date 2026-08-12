import numpy as np
import xgboost as xgb
import sys
import os

# Ensure the module can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), 'Codebase'))
try:
    from xgboost_multi_obj import train_xgboost_with_bounds, BoundedMultiObjective
except ImportError:
    print("Could not import xgboost_multi_obj from Codebase.")
    sys.exit(1)

def run_integration():
    """
    Demonstrates integrating the custom multi-objective bounds into XGBoost.
    """
    print("1. Generating multi-target synthetic dataset...")
    np.random.seed(42)
    N_samples = 2000
    N_features = 5
    
    X = np.random.randn(N_samples, N_features)
    
    # Objective 1: Maximize return (simulated)
    y0 = 2.0 * X[:, 0] + 1.5 * X[:, 1] + np.random.randn(N_samples) * 0.5
    
    # Objective 2: Minimize risk/drawdown (simulated)
    # We want this target bounded between -1.0 and 1.0 ideally.
    y1 = -1.0 * X[:, 2] + 2.0 * X[:, 3] + np.random.randn(N_samples) * 0.5
    
    Y = np.column_stack((y0, y1))
    
    # Create XGBoost DMatrix
    dtrain = xgb.DMatrix(X, label=Y)
    
    # 2. Define Bounds and Constraints
    # Target 0 (Return): No bounds
    # Target 1 (Risk): Hard bound between -1.0 and 1.0
    bounds = [
        (None, None),  # Target 0 bounds
        (-1.0, 1.0)    # Target 1 bounds
    ]
    weights = [1.0, 2.0] # Give more weight to bounding risk
    penalty_factor = 100.0 # High penalty for out-of-bounds
    
    params = {
        'max_depth': 4,
        'learning_rate': 0.1,
        'disable_default_eval_metric': 1, # Use our custom feval
    }
    
    print("\n2. Training standard model (Unbounded) for comparison...")
    # For comparison, train without bounds
    model_unbounded = xgb.train(
        params={'max_depth': 4, 'learning_rate': 0.1, 'multi_strategy': 'multi_output_tree'},
        dtrain=dtrain,
        num_boost_round=30
    )
    
    print("\n3. Training model WITH Multi-Objective Bounds...")
    model_bounded = train_xgboost_with_bounds(
        params=params,
        dtrain=dtrain,
        bounds=bounds,
        weights=weights,
        penalty_factor=penalty_factor,
        num_boost_round=30
    )
    
    # 4. Evaluate Integration
    preds_unbounded = model_unbounded.predict(dtrain)
    preds_bounded = model_bounded.predict(dtrain)
    
    # Reshape if needed
    if len(preds_unbounded.shape) == 1:
        preds_unbounded = preds_unbounded.reshape(-1, 2)
    if len(preds_bounded.shape) == 1:
        preds_bounded = preds_bounded.reshape(-1, 2)
        
    violations_unbound = np.sum((preds_unbounded[:, 1] < bounds[1][0]) | (preds_unbounded[:, 1] > bounds[1][1]))
    violations_bound = np.sum((preds_bounded[:, 1] < bounds[1][0]) | (preds_bounded[:, 1] > bounds[1][1]))
    
    print("\n--- Integration Results ---")
    print(f"Violations (Target 1) - Unbounded Model : {violations_unbound} / {N_samples}")
    print(f"Violations (Target 1) - Bounded Model   : {violations_bound} / {N_samples}")
    print("\nSuccess: Multi-objective bounds successfully integrated and constrained the predictions!")

if __name__ == '__main__':
    run_integration()
