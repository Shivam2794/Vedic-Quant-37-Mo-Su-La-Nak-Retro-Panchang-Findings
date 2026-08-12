import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import xgboost as xgb
import os
import warnings
warnings.filterwarnings('ignore')

class SAE(nn.Module):
    def __init__(self, input_dim, latent_dim):
        super().__init__()
        self.enc = nn.Linear(input_dim, latent_dim)
        self.relu = nn.ReLU()
        self.dec = nn.Linear(latent_dim, input_dim)
        
    def forward(self, x):
        h = self.relu(self.enc(x))
        return self.dec(h), h

def train_sae(model, X, epochs=10, lr=1e-3, l1_lambda=1e-5):
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()
    model.train()
    dataset = torch.utils.data.TensorDataset(X)
    loader = torch.utils.data.DataLoader(dataset, batch_size=128, shuffle=True)
    
    for epoch in range(epochs):
        epoch_loss = 0.0
        for batch in loader:
            x = batch[0]
            optimizer.zero_grad()
            x_hat, h = model(x)
            loss = criterion(x_hat, x) + l1_lambda * h.abs().mean()
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        print(f"SAE Epoch {epoch+1}/{epochs}, Loss: {epoch_loss/len(loader):.4f}")

def main():
    print("Loading actual dataset...")
    dataset_candidates = ['advanced_ml_dataset.csv', 'orion_master_dataset.csv', 'master_feature_matrix.parquet']
    df = None
    for cand in dataset_candidates:
        if os.path.exists(cand):
            try:
                if cand.endswith('.csv'):
                    df = pd.read_csv(cand)
                else:
                    df = pd.read_parquet(cand)
                print(f"Successfully loaded {cand}")
                break
            except Exception as e:
                pass
                
    if df is None:
        print("Dataset not found!")
        return

    # Process Date to get Year
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df['Year'] = df['Date'].dt.year
    elif 'Transit_Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Transit_Date'])
        df['Year'] = df['Date'].dt.year
    else:
        print("No Date column found!")
        return
        
    df = df.sort_values('Date').reset_index(drop=True)
    
    # Identify Target and Return
    if 'Target_Label' in df.columns:
        target_col = 'Target_Label'
        df['Binary_Target'] = (df[target_col] > 0).astype(int)
        df['Daily_Return'] = df['Close'].pct_change().shift(-1).fillna(0)
    elif 'Target_Forward_5D_Return' in df.columns:
        target_col = 'Target_Forward_5D_Return'
        df['Binary_Target'] = (df[target_col] > 0).astype(int)
        df['Daily_Return'] = df['SPY_Close'].pct_change().shift(-1).fillna(0)
    else:
        print("No valid target column found.")
        return
        
    # Drop non-feature columns
    exclude = ['Date', 'Year', 'Target_Label', 'Target_Forward_5D_Return', 'Target_Crash_Flag', 
               'Close', 'SPY_Close', 'ATR_pct', 'Binary_Target', 'Daily_Return', 'Transit_Date', 'Asset', 'Ticker', 'Type']
    feature_cols = [c for c in df.columns if c not in exclude]
    
    # One-hot encode
    print("One-hot encoding...")
    X_df = pd.get_dummies(df[feature_cols])
    X_df = X_df.fillna(0)
    
    input_dim = X_df.shape[1]
    print(f"Features found: {input_dim}")
    
    if input_dim != 1013:
        print(f"Adjusting features to exactly 1013...")
        if input_dim < 1013:
            for i in range(1013 - input_dim):
                X_df[f'pad_{i}'] = 0.0
        else:
            X_df = X_df.iloc[:, :1013]
    
    # Split
    train_idx = df['Year'] <= 2005
    test_idx = df['Year'] >= 2006
    
    if not train_idx.any() or not test_idx.any():
        print("Train or test set is empty! Check year ranges.")
        return
        
    X_train = X_df[train_idx].values
    y_train = df.loc[train_idx, 'Binary_Target'].values
    X_test = X_df[test_idx].values
    y_test = df.loc[test_idx, 'Binary_Target'].values
    returns_test = df.loc[test_idx, 'Daily_Return'].values
    
    print(f"Train samples: {len(X_train)}, Test samples: {len(X_test)}")
    
    # Scale
    print("Scaling...")
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    X_train_t = torch.FloatTensor(X_train_scaled)
    X_test_t = torch.FloatTensor(X_test_scaled)
    
    # SAE
    sae = SAE(1013, 2048)
    train_sae(sae, X_train_t, epochs=10)
    
    sae.eval()
    with torch.no_grad():
        _, train_latents = sae(X_train_t)
        _, test_latents = sae(X_test_t)
        
    # XGBoost
    print("Training XGBoost...")
    xgb_clf = xgb.XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.1, random_state=42)
    xgb_clf.fit(train_latents.numpy(), y_train)
    
    # Predict
    print("Predicting...")
    test_probs = xgb_clf.predict_proba(test_latents.numpy())[:, 1]
    
    # Strategy
    positions = (test_probs > 0.52).astype(int)
    
    # Metrics
    accuracy = (positions == y_test).mean()
    strategy_returns = positions * returns_test
    
    cum_returns = np.cumprod(1 + strategy_returns)
    total_return = cum_returns[-1] - 1 if len(cum_returns) > 0 else 0
    years = (df.loc[test_idx, 'Date'].max() - df.loc[test_idx, 'Date'].min()).days / 365.25
    cagr = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
    
    roll_max = np.maximum.accumulate(cum_returns)
    drawdowns = cum_returns / roll_max - 1
    max_dd = drawdowns.min() if len(drawdowns) > 0 else 0
    
    print("\n--- Results ---")
    print(f"Accuracy: {accuracy:.4%}")
    print(f"CAGR: {cagr:.4%}")
    print(f"Drawdown: {max_dd:.4%}")

if __name__ == "__main__":
    main()
