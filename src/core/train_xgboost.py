import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt
import os

def train_model():
    print("Loading Architected ML Dataset...")
    df = pd.read_csv("architected_ml_dataset.csv", index_col="Date")
    
    # Filter to binary classification for clearer signal (Drop sideways '0' labels)
    df = df[df['Target_Label'] != 0.0]
    
    # Map -1 to 0 for XGBoost
    df['Target_Label'] = df['Target_Label'].map({-1.0: 0, 1.0: 1})
    
    print(f"Dataset shape after filtering: {df.shape}")
    
    # Features and Target
    X = df.drop(columns=['Target_Label', 'Close', 'ATR_pct'])
    y = df['Target_Label']
    
    # Force one-hot encoding on any remaining string/object columns
    X = pd.get_dummies(X)
    
    # Purged CV to prevent overlapping rows and look-ahead leakage
    from sklearn.model_selection import TimeSeriesSplit
    purge_gap = 20
    tscv = TimeSeriesSplit(n_splits=5, gap=purge_gap)
    
    # Initialize XGBoost with Brutal Anti-Overfitting
    # max_depth=3 (very shallow trees to prevent memorizing exact dates)
    # reg_alpha=1.0 (L1 regularization to drop useless planets)
    # reg_lambda=2.0 (L2 regularization to smooth weights)
    # learning_rate=0.01 (slow learning)
    model = XGBClassifier(
        n_estimators=300,
        max_depth=3,
        learning_rate=0.01,
        reg_alpha=2.0,
        reg_lambda=5.0,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='logloss'
    )
    
    print("\nTraining XGBoost Model with Purged CV...")
    y_tests = []
    y_preds = []
    
    for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
        X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
        X_test, y_test = X.iloc[test_idx], y.iloc[test_idx]
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        y_tests.extend(y_test)
        y_preds.extend(y_pred)
        
        fold_acc = accuracy_score(y_test, y_pred)
        print(f"Fold {fold+1} Accuracy: {fold_acc:.4f}")
    
    acc = accuracy_score(y_tests, y_preds)
    print(f"\nOverall CV Accuracy: {acc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_tests, y_preds))
    
    # Feature Importance Extraction (on the last fold model)
    importances = model.feature_importances_
    feat_imp = pd.Series(importances, index=X.columns).sort_values(ascending=False)
    
    print("\nTop 15 Most Predictive Astrological Features:")
    print(feat_imp.head(15))
    
    # Save the output report
    with open("ml_report.txt", "w") as f:
        f.write(f"Overall CV Accuracy: {acc:.4f}\n\n")
        f.write("Classification Report:\n")
        f.write(classification_report(y_tests, y_preds))
        f.write("\nTop 15 Astrological Features:\n")
        f.write(feat_imp.head(15).to_string())

if __name__ == "__main__":
    train_model()
