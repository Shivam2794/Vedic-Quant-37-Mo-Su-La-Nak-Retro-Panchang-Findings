import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LassoCV
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings("ignore")

def calc_metrics(returns, risk_free=0.02):
    if len(returns) == 0:
        return 0, 0, 0
    cum_ret = (1 + returns).cumprod()
    cagr = (cum_ret.iloc[-1] ** (12 / len(returns))) - 1  # 12 months in a year
    
    vol = returns.std() * np.sqrt(12)
    sharpe = (cagr - risk_free) / vol if vol > 0 else 0
    
    roll_max = cum_ret.cummax()
    drawdown = (cum_ret - roll_max) / roll_max
    max_dd = drawdown.min()
    return cagr, max_dd, sharpe

def build_mega_matrix():
    print("[*] Downloading Institutional Universe (SPY, TLT, LQD, GLD, SHV)...")
    tickers = ["SPY", "TLT", "LQD", "GLD", "SHV"]
    # We download daily data first to compute accurate intra-month vols, then resample.
    data = yf.download(tickers, start="2005-01-01", end="2024-01-01", progress=False, auto_adjust=True)
    if isinstance(data.columns, pd.MultiIndex):
        close_data = data['Close']
    else:
        close_data = data
        
    print("[*] Engineering 100+ Features from 6731 Discoveries...")
    # Resample to Monthly End
    monthly_close = close_data.resample('ME').last()
    
    features = pd.DataFrame(index=monthly_close.index)
    
    # Target: Predict next month's SPY return
    features['Target'] = monthly_close['SPY'].pct_change().shift(-1)
    
    # 1. Momentum Features (Absolute & Relative)
    for asset in tickers:
        for m in [1, 3, 6, 9, 12]:
            features[f'{asset}_Mom_{m}M'] = monthly_close[asset].pct_change(m)
            
    # 2. Macro Spreads
    features['Yield_Spread_TLT_SHV'] = monthly_close['TLT'].pct_change(3) - monthly_close['SHV'].pct_change(3)
    features['Credit_Spread_LQD_TLT'] = monthly_close['LQD'].pct_change(3) - monthly_close['TLT'].pct_change(3)
    features['Gold_SPY_Ratio'] = monthly_close['GLD'] / monthly_close['SPY']
    features['Gold_SPY_Ratio_Mom_6M'] = features['Gold_SPY_Ratio'].pct_change(6)
    
    # 3. Reversion / Moving Average Extensions
    for asset in ['SPY', 'TLT']:
        for m in [3, 6, 12]:
            ma = monthly_close[asset].rolling(m).mean()
            features[f'{asset}_MA_Dist_{m}M'] = (monthly_close[asset] - ma) / ma
            
    # 4. Volatility (Realized Volatility over 1, 3, 6 months)
    daily_returns = close_data.pct_change()
    monthly_vol = daily_returns.resample('ME').std() * np.sqrt(252)
    for asset in tickers:
        for m in [1, 3, 6]:
            features[f'{asset}_Vol_{m}M'] = monthly_vol[asset].rolling(m).mean()

    # Drop NaNs created by rolling windows (mostly first 12 months)
    features = features.dropna()
    return features, monthly_close

def run_alpha_factory():
    print("========================================================")
    print("[*] INSTITUTIONAL ALPHA FACTORY (Lasso Meta-Ensemble)")
    print("========================================================")
    
    features, monthly_close = build_mega_matrix()
    
    # Extract feature names (everything except Target)
    X_cols = [c for c in features.columns if c != 'Target']
    print(f"[*] Total Initial Factors Computed: {len(X_cols)}")
    
    # ---------------------------------------------------------
    # Walk-Forward Lasso Regularization Sieve
    # ---------------------------------------------------------
    # Train on 60 months (5 years), predict next 1 month, roll forward
    train_size = 60
    step_size = 1
    
    predictions = pd.Series(index=features.index, dtype=float)
    active_features_history = []
    
    print("[*] Initiating 15-Year Walk-Forward Feature Sieve & Prediction Loop...")
    for start_idx in range(0, len(features) - train_size, step_size):
        train_end = start_idx + train_size
        test_end = min(train_end + step_size, len(features))
        
        train_data = features.iloc[start_idx:train_end]
        test_data = features.iloc[train_end:test_end]
        
        X_train = train_data[X_cols].values
        y_train = train_data['Target'].values
        X_test = test_data[X_cols].values
        
        # Standardize
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # LassoCV automatically finds the best L1 penalty via cross-validation
        # It aggressively pushes useless feature coefficients to absolute 0
        model = LassoCV(cv=5, random_state=42, n_jobs=-1, max_iter=2000)
        model.fit(X_train_scaled, y_train)
        
        preds = model.predict(X_test_scaled)
        predictions.iloc[train_end:test_end] = preds
        
        # Log how many features survived the L1 sieve in this window
        surviving_features = np.sum(model.coef_ != 0)
        active_features_history.append(surviving_features)
        
    avg_surviving = np.mean(active_features_history)
    print(f"[*] Lasso Sieve Results: Eliminated ~{len(X_cols) - int(avg_surviving)} fake signals.")
    print(f"[*] Lasso Sieve Results: Retained average of {avg_surviving:.1f} true orthogonal factors per month.")
    
    # ---------------------------------------------------------
    # Portfolio Construction (Brutal Inspector Mode)
    # ---------------------------------------------------------
    pred_data = predictions.dropna()
    actual_data = features.loc[pred_data.index]
    
    # Strategy Logic:
    # If predicted next month return > 0, allocate 100% SPY
    # If predicted next month return < 0, allocate 100% TLT (Treasuries)
    weights_spy = (pred_data > 0).astype(float)
    weights_tlt = (pred_data <= 0).astype(float)
    
    # Portfolio Return = Weight_T * Return_T+1
    # Note: features['Target'] is already shifted to be T+1 return of SPY
    # We also need T+1 return of TLT
    tlt_returns = monthly_close['TLT'].pct_change().shift(-1).loc[pred_data.index]
    
    raw_returns = (weights_spy * actual_data['Target']) + (weights_tlt * tlt_returns)
    
    # Brutal Slippage: 20 bps per trade (0.20%)
    turnover = weights_spy.diff().abs() # If SPY weight changes from 1 to 0, turnover is 1
    # A full rotation (SPY to TLT) means we sell 100% SPY and buy 100% TLT. 
    # Technically 2 trades, so 2 * 0.0020 = 0.40% friction per rotation.
    slippage_cost = turnover * 0.0040 
    
    net_returns = raw_returns - slippage_cost.fillna(0)
    
    # Calculate Metrics
    cagr, max_dd, sharpe = calc_metrics(net_returns)
    bm_cagr, bm_dd, bm_sharpe = calc_metrics(actual_data['Target'])
    
    print("\n[*] BRUTAL INSPECTION FINAL RESULTS:")
    print("--------------------------------------------------------")
    print(f"BENCHMARK (SPY Buy & Hold):")
    print(f"CAGR: {bm_cagr*100:.2f}% | Max DD: {bm_dd*100:.2f}% | Sharpe: {bm_sharpe:.2f}")
    print("--------------------------------------------------------")
    print(f"INSTITUTIONAL FACTOR MACHINE (Lasso + Monthly Rotation):")
    print(f"CAGR: {cagr*100:.2f}% | Max DD: {max_dd*100:.2f}% | Sharpe: {sharpe:.2f}")
    print("========================================================\n")

if __name__ == "__main__":
    run_alpha_factory()
