"""
Phase 3: Tabular Baseline Training
==================================
Trains an XGBoost baseline model using ONLY the 27 mathematically 
proven causal features from Phase 2 (PCMCI). 

Evaluates using Time Series Split (Walk-Forward Validation) to 
generate a baseline Sharpe ratio for the 63-day horizon.
"""
import pandas as pd
import numpy as np
import subprocess
import json
import io
import os
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

BQ_CMD = r"C:\Users\Shivam Patel\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd"
CAUSAL_CORE_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\causal_core.csv"
RETURNS_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_returns.parquet"

def run_query(sql):
    tmp_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\tmp_features.csv"
    cmd = f'"{BQ_CMD}" query --use_legacy_sql=false --format=csv --max_rows=1000000 "{sql}" > "{tmp_path}"'
    print(f"  [run_query] Invoking cmd...", flush=True)
    result = subprocess.run(cmd, shell=True)
    print(f"  [run_query] Cmd finished with code {result.returncode}", flush=True)
    if result.returncode != 0:
        raise RuntimeError("BQ Query Failed")
    df = pd.read_csv(tmp_path)
    os.remove(tmp_path)
    return df

def calculate_sharpe(returns, risk_free_rate=0.0):
    """Annualized Sharpe Ratio for Daily Returns"""
    if len(returns) == 0 or np.std(returns) == 0:
        return 0.0
    daily_sharpe = (np.mean(returns) - risk_free_rate) / np.std(returns)
    return daily_sharpe * np.sqrt(252)

def train_baseline():
    print("="*50, flush=True)
    print("PHASE 3: TABULAR BASELINE (XGBoost)", flush=True)
    print("="*50, flush=True)

    # 1. Load the 27 Causal Features
    if not os.path.exists(CAUSAL_CORE_PATH):
        print("ERROR: causal_core.csv not found. Run Phase 2 first.", flush=True)
        return
        
    core_df = pd.read_csv(CAUSAL_CORE_PATH)
    features = core_df['feature'].tolist()
    print(f"Loaded {len(features)} causal features from PCMCI.", flush=True)
    
    # 2. Query BigQuery for exactly these features
    print("Querying Feature Matrix from BigQuery...", flush=True)
    feature_cols = ", ".join(features)
    sql = f"SELECT ticker, date, {feature_cols} FROM `antigravity_quant.feature_matrix` WHERE RAND() < 0.1 ORDER BY date"
    
    print(f"Executing BQ Query via CLI...", flush=True)
    df_features = run_query(sql)
    df_features['date'] = pd.to_datetime(df_features['date']).dt.date.astype(str)
    print(f"Downloaded {len(df_features)} rows of feature data.")

    # 3. Load Local Returns
    print("Loading Local Returns Matrix...")
    df_returns = pd.read_parquet(RETURNS_PATH)
    df_returns['date'] = pd.to_datetime(df_returns['date']).dt.date.astype(str)
    
    # 4. Merge Features and Targets
    target = 'fwd_return_63d'
    merged = df_features.merge(df_returns[['ticker', 'date', target]], 
                               on=['ticker', 'date'], how='inner')
    merged = merged.dropna()
    merged['date'] = pd.to_datetime(merged['date'])
    merged = merged.sort_values('date').reset_index(drop=True)
    
    print(f"Final training matrix shape: {merged.shape}")
    
    # 5. Walk-Forward Validation (Time Series Split)
    X = merged[features]
    y = merged[target]
    
    tscv = TimeSeriesSplit(n_splits=5)
    model = xgb.XGBRegressor(
        n_estimators=100,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.8,
        colsample_bytree=0.8,
        n_jobs=-1,
        random_state=42
    )
    
    print("\nExecuting Walk-Forward Validation (5 folds)...")
    fold_sharpes = []
    
    for fold, (train_index, test_index) in enumerate(tscv.split(X)):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        
        # Simple Strategy: Go long if predicted return > 0
        # Simulated strategy return = actual return * direction
        # Since it's a 63D return, we look at the average PnL of these 63D signals
        
        signals = np.where(predictions > 0, 1, 0)
        # only take trades where we get a signal
        strategy_returns = y_test[signals == 1] 
        
        # We approximate a portfolio return by looking at the mean 63D return of the selected basket
        if len(strategy_returns) > 0:
            # Scale to daily equivalent for standard sharpe calculation
            daily_equivalent_returns = strategy_returns / 63.0 
            sharpe = calculate_sharpe(daily_equivalent_returns)
        else:
            sharpe = 0.0
            
        fold_sharpes.append(sharpe)
        print(f"  Fold {fold+1}: Trades={len(strategy_returns)}/{len(y_test)} | Sharpe: {sharpe:.2f}")

    avg_sharpe = np.mean(fold_sharpes)
    print("\n" + "="*50)
    print(f"BASELINE XGBOOST STRATEGY (63D Horizon)")
    print(f"Mean Walk-Forward Sharpe Ratio: {avg_sharpe:.2f}")
    print("="*50)
    
    # Feature Importance on full dataset
    model.fit(X, y)
    imp = pd.DataFrame({
        'Feature': features,
        'Importance': model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    print("\nTop 10 Important Causal Features (XGBoost):")
    print(imp.head(10).to_string(index=False))

if __name__ == "__main__":
    train_baseline()
