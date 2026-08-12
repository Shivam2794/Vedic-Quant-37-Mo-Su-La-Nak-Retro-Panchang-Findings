import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import accuracy_score, precision_score, classification_report
import os
import pickle

def train_meta_labeler(ticker):
    print(f"[{ticker}] Training V18 XGBoost Meta-Labeler on Latent States...")
    trades_file = f"{ticker}_V18_trades.parquet"
    latent_file = f"{ticker}_daily_V18_latent.parquet"
    
    if not os.path.exists(trades_file) or not os.path.exists(latent_file):
        print("Missing trades or latent files. Run encoder and grinder first.")
        return
        
    df_trades = pd.read_parquet(trades_file)
    df_latent = pd.read_parquet(latent_file)
    
    if len(df_trades) < 50:
        print(f"Not enough trades ({len(df_trades)}) for Meta-Labeling.")
        return
        
    # Build Dataset
    # Target: 1 if return > 0 else 0
    df_trades['target'] = (df_trades['return'] > 0).astype(int)
    
    latent_cols = [c for c in df_latent.columns if c.startswith('Latent_')]
    
    # We must match the latent states to the day before entry (or day of entry, since latent state is derived from T-1 close)
    # The latent state at T is available for prediction at T.
    features = []
    targets = []
    for idx, row in df_trades.iterrows():
        entry_date = row['entry_date']
        # Get latent state for this date
        try:
            latent_state = df_latent.loc[entry_date, latent_cols].values
            features.append(latent_state)
            targets.append(row['target'])
        except KeyError:
            continue
            
    X = np.array(features)
    y = np.array(targets)
    
    # Walk-forward split
    train_size = int(len(X) * 0.7)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    # Class weights for imbalanced data
    pos_weight = (len(y_train) - sum(y_train)) / max(1, sum(y_train))
    
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=3, # keep shallow to prevent overfitting
        learning_rate=0.05,
        scale_pos_weight=pos_weight,
        eval_metric='logloss',
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    
    print(f"[{ticker}] Meta-Labeler OOS Accuracy:  {acc:.2%}")
    print(f"[{ticker}] Meta-Labeler OOS Precision: {prec:.2%}")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Analyze Kelly Fraction
    # Win rate of trades that XGBoost approves
    approved_trades = y_test[y_pred == 1]
    if len(approved_trades) > 0:
        meta_win_rate = sum(approved_trades) / len(approved_trades)
        print(f"[{ticker}] Win rate of approved trades: {meta_win_rate:.2%}")
        
        # Calculate Kelly Fraction (assuming roughly equal win/loss magnitude from SL/TP ratio)
        # Average Win / Average Loss
        train_trades = df_trades.iloc[:train_size]
        avg_win = train_trades[train_trades['return'] > 0]['return'].mean()
        avg_loss = abs(train_trades[train_trades['return'] < 0]['return'].mean())
        
        if avg_loss > 0 and len(approved_trades) > 5:
            payoff_ratio = avg_win / avg_loss
            kelly = meta_win_rate - ((1 - meta_win_rate) / payoff_ratio)
            # Cap Kelly at 10%
            kelly = max(0.0, min(kelly, 0.10))
            print(f"[{ticker}] Optimal Fractional Kelly (capped at 10%): {kelly:.2%}")
        else:
            print("Not enough data for Kelly sizing.")
    else:
        print(f"[{ticker}] Model approved NO OOS trades.")
        
    # Save Model
    model_file = f"{ticker}_V18_metalabeler.pkl"
    with open(model_file, 'wb') as f:
        pickle.dump(model, f)
    print(f"[{ticker}] Model saved to {model_file}")

if __name__ == '__main__':
    train_meta_labeler('SPY')
