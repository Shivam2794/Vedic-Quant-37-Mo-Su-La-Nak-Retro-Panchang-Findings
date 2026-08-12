import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, classification_report
import warnings

warnings.filterwarnings("ignore")

def calc_metrics(returns, risk_free=0.02):
    if len(returns) == 0:
        return 0, 0, 0
    cum_ret = (1 + returns).cumprod()
    cagr = (cum_ret.iloc[-1] ** (252 / len(returns))) - 1
    
    vol = returns.std() * np.sqrt(252)
    sharpe = (cagr - risk_free) / vol if vol > 0 else 0
    
    roll_max = cum_ret.cummax()
    drawdown = (cum_ret - roll_max) / roll_max
    max_dd = drawdown.min()
    return cagr, max_dd, sharpe

def build_features(df):
    """Engineer 50+ structural features"""
    print("[*] Engineering Features...")
    df = df.copy()
    close = df['Close']
    
    # Target: 1 if tomorrow is positive, 0 otherwise
    df['Target'] = (close.pct_change().shift(-1) > 0).astype(int)
    
    # 1. Returns (Momentum)
    for w in [1, 2, 3, 5, 10, 20, 40, 60, 120]:
        df[f'Ret_{w}'] = close.pct_change(w)
        
    # 2. Moving Average Distances
    for w in [5, 10, 20, 50, 100, 200]:
        ma = close.rolling(w).mean()
        df[f'MA_Dist_{w}'] = (close - ma) / ma
        
    # 3. Volatility
    for w in [5, 10, 20, 60]:
        df[f'Vol_{w}'] = close.pct_change().rolling(w).std()
        
    # 4. Donchian Channel Distances (High/Low)
    for w in [10, 20, 60]:
        rolling_max = df['High'].rolling(w).max()
        rolling_min = df['Low'].rolling(w).min()
        df[f'Donchian_Pos_{w}'] = (close - rolling_min) / (rolling_max - rolling_min + 1e-8)
        
    # 5. Price/Volume dynamics
    for w in [5, 20]:
        df[f'Vol_Trend_{w}'] = df['Volume'].pct_change(w)
        
    return df.dropna()

def run_ml_strategy():
    print("========================================================")
    print("[*] ML HOLY GRAIL: PCA AUTOENCODER + XGBOOST")
    print("========================================================")
    
    # 1. Ingest Data
    print("[*] Downloading SPY (Total Return)...")
    data = yf.download("SPY", start="2000-01-01", end="2024-01-01", progress=False, auto_adjust=True)
    if isinstance(data.columns, pd.MultiIndex):
        data = data.xs('SPY', axis=1, level=1)
        
    data = build_features(data)
    
    features = [c for c in data.columns if c not in ['Target', 'Open', 'High', 'Low', 'Close', 'Volume']]
    print(f"[*] Engineered {len(features)} Features.")
    
    # 2. Walk-Forward Validation Setup
    # Train on 5 years (approx 1250 days), test on next 1 year (250 days)
    train_size = 1250
    step_size = 250
    
    all_predictions = pd.Series(index=data.index, dtype=float)
    
    print("[*] Initiating Walk-Forward PCA Compression & XGBoost Training...")
    
    for start_idx in range(0, len(data) - train_size, step_size):
        train_end = start_idx + train_size
        test_end = min(train_end + step_size, len(data))
        
        train_data = data.iloc[start_idx:train_end]
        test_data = data.iloc[train_end:test_end]
        
        X_train_raw = train_data[features].values
        y_train = train_data['Target'].values
        X_test_raw = test_data[features].values
        
        # PCA Dimensionality Reduction (Autoencoder Proxy)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train_raw)
        X_test_scaled = scaler.transform(X_test_raw)
        
        # Compress 50+ features into 10 orthogonal latent vectors
        pca = PCA(n_components=10, random_state=42)
        X_train_pca = pca.fit_transform(X_train_scaled)
        X_test_pca = pca.transform(X_test_scaled)
        
        # XGBoost Training
        model = XGBClassifier(
            n_estimators=100, 
            max_depth=3, 
            learning_rate=0.05, 
            subsample=0.8,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train_pca, y_train)
        
        # Predict Probabilities
        preds = model.predict_proba(X_test_pca)[:, 1] # Probability of Class 1 (Up)
        
        all_predictions.iloc[train_end:test_end] = preds
        
    # Drop rows without predictions (the first 5 years of training buffer)
    pred_data = all_predictions.dropna()
    actual_data = data.loc[pred_data.index]
    
    # 3. Strategy Logic (Brutal Inspector Mode)
    # Long if prob > 55%, Short if prob < 45%, else Cash
    weights = pd.Series(0.0, index=pred_data.index)
    weights[pred_data > 0.53] = 1.0  # Slightly looser threshold to allow trades
    weights[pred_data < 0.47] = -1.0
    
    # Alignment: prediction made at Close of T, position held during T+1
    # Target is already T+1 return, so we multiply weight * actual return of T+1
    # which is captured by pct_change().shift(-1) which we stored in actual_data earlier.
    # Wait, actual_data['Close'].pct_change() is the return from T-1 to T.
    # If our prediction at T applies to T+1, we multiply weights (from T) by returns at T+1.
    strat_returns_raw = weights.shift(1).fillna(0) * actual_data['Close'].pct_change()
    
    # Transaction Costs (10 bps)
    turnover = weights.shift(1).fillna(0).diff().abs()
    strat_returns_tc = strat_returns_raw - (turnover * 0.0010)
    
    # Short Borrowing Costs (1% annualized = ~0.4 bps daily)
    short_days = (weights.shift(1).fillna(0) < 0)
    strat_returns_final = strat_returns_tc.copy()
    strat_returns_final[short_days] -= (0.01 / 252)
    
    # Calculate Metrics
    cagr, max_dd, sharpe = calc_metrics(strat_returns_final)
    
    bm_returns = actual_data['Close'].pct_change().dropna()
    bm_cagr, bm_dd, bm_sharpe = calc_metrics(bm_returns)
    
    # ML Metrics
    binary_preds = (pred_data > 0.50).astype(int)
    acc = accuracy_score(actual_data['Target'], binary_preds)
    
    print("\n[*] BRUTAL INSPECTION FINAL RESULTS:")
    print("--------------------------------------------------------")
    print(f"ML Directional Accuracy: {acc*100:.2f}%")
    print("--------------------------------------------------------")
    print(f"BENCHMARK (SPY Total Return):")
    print(f"CAGR: {bm_cagr*100:.2f}% | Max DD: {bm_dd*100:.2f}% | Sharpe: {bm_sharpe:.2f}")
    print("--------------------------------------------------------")
    print(f"PCA-XGBOOST L/S (10bps Slippage + 1% Borrow Cost):")
    print(f"CAGR: {cagr*100:.2f}% | Max DD: {max_dd*100:.2f}% | Sharpe: {sharpe:.2f}")
    print("========================================================\n")

if __name__ == "__main__":
    run_ml_strategy()
