import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import accuracy_score, precision_score, classification_report
import os
import pickle

def train_meta_labeler(ticker):
    print(f"[{ticker}] Training V20 XGBoost Meta-Labeler on Latent States (Fixed Chronological Split)...")
    trades_file = f"{ticker}_V20_trades.parquet"
    latent_file = f"{ticker}_daily_V20_latent.parquet"
    
    if not os.path.exists(trades_file) or not os.path.exists(latent_file):
        print("Missing trades or latent files. Run encoder and grinder first.")
        return
        
    df_trades = pd.read_parquet(trades_file)
    df_latent = pd.read_parquet(latent_file)
    
    if len(df_trades) < 50:
        print(f"Not enough trades ({len(df_trades)}) for Meta-Labeling.")
        return
        
    # We must split the TRADES by the actual Out-Of-Sample date from the latent encoder/grinder.
    # The latent encoder and grinder both used 70% of the BARS as the In-Sample period.
    train_bars = int(len(df_latent) * 0.7)
    oos_start_date = df_latent.index[train_bars]
    print(f"[{ticker}] Walk-Forward OOS Date cutoff is: {oos_start_date.date()}")
    
    df_trades['target'] = (df_trades['return'] > 0).astype(int)
    latent_cols = [c for c in df_latent.columns if c.startswith('Latent_')]
    
    # Extract features matching the exact entry dates
    features = []
    targets = []
    dates = []
    
    for idx, row in df_trades.iterrows():
        entry_date = row['entry_date']
        try:
            latent_state = df_latent.loc[entry_date, latent_cols].values
            features.append(latent_state)
            targets.append(row['target'])
            dates.append(entry_date)
        except KeyError:
            continue
            
    df_dataset = pd.DataFrame(features, columns=latent_cols)
    df_dataset['target'] = targets
    df_dataset['entry_date'] = dates
    
    # Split exactly by the chronological OOS start date to prevent leakage!
    train_df = df_dataset[df_dataset['entry_date'] < oos_start_date]
    test_df = df_dataset[df_dataset['entry_date'] >= oos_start_date]
    
    if len(test_df) == 0 or len(train_df) == 0:
        print("Not enough trades in either train or test split. Aborting.")
        return
        
    X_train = train_df[latent_cols].values
    y_train = train_df['target'].values
    X_test = test_df[latent_cols].values
    y_test = test_df['target'].values
    
    # Class weights for imbalanced data
    pos_weight = (len(y_train) - sum(y_train)) / max(1, sum(y_train))
    
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=3, # keep shallow to prevent overfitting
        learning_rate=0.05,
        eval_metric='logloss',
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    
    print(f"[{ticker}] Meta-Labeler OOS Accuracy:  {acc:.2%}")
    print(f"[{ticker}] Meta-Labeler OOS Precision: {prec:.2%}")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Calculate fractional Kelly
    approved_trades = y_test[y_pred == 1]
    if len(approved_trades) > 0:
        meta_win_rate = sum(approved_trades) / len(approved_trades)
        print(f"[{ticker}] Win rate of approved trades: {meta_win_rate:.2%}")
        
        # Win/Loss magnitude from TRAIN ONLY
        train_trades = df_trades[df_trades['entry_date'] < oos_start_date]
        avg_win = train_trades[train_trades['return'] > 0]['return'].mean()
        avg_loss = abs(train_trades[train_trades['return'] < 0]['return'].mean())
        
        if avg_loss > 0 and len(approved_trades) > 5:
            payoff_ratio = avg_win / avg_loss
            kelly = meta_win_rate - ((1 - meta_win_rate) / payoff_ratio)
            kelly = max(0.0, min(kelly, 0.10)) # Cap at 10%
            print(f"[{ticker}] Optimal Fractional Kelly (capped at 10%): {kelly:.2%}")
        else:
            print("Not enough data for Kelly sizing.")
    else:
        print(f"[{ticker}] Model approved NO OOS trades.")
        
    # Predict over ALL trades to save back to parquet so the Portfolio Architect can filter them
    all_X = df_dataset[latent_cols].values
    all_preds = model.predict(all_X)
    df_trades['meta_label_approve'] = all_preds
    
    df_trades.to_parquet(trades_file)
    print(f"[{ticker}] Added 'meta_label_approve' column to {trades_file}")
    
    model_file = f"{ticker}_V20_metalabeler.pkl"
    with open(model_file, 'wb') as f:
        pickle.dump(model, f)
    print(f"[{ticker}] Model saved to {model_file}")

if __name__ == '__main__':
    train_meta_labeler('SPY')
