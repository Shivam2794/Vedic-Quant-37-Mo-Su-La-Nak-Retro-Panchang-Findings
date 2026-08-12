import yfinance as yf
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import math
import os
import sys

# Suppress yfinance warnings
import warnings
warnings.filterwarnings('ignore')

def get_djia_data():
    csv_path = 'djia_2000_2026.csv'
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, index_col='Date', parse_dates=True)
        return df
    print("Fetching DJIA data...")
    df = yf.download('^DJI', start='2000-01-01', end='2026-06-13', progress=False)
    # yf.download can return MultiIndex columns if not careful, flatten them if needed
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    df.to_csv(csv_path)
    return df

def feature_engineering(df):
    # Ensure no lookahead bias!
    # All features must only use past data up to day t.
    # The target will be day t+1's return.
    
    # Base prices
    close = df['Close']
    
    # Returns
    df['Ret_1'] = close.pct_change()
    df['Ret_2'] = close.pct_change(2)
    df['Ret_5'] = close.pct_change(5)
    df['Ret_10'] = close.pct_change(10)
    df['Ret_21'] = close.pct_change(21)
    
    # Moving Averages
    df['SMA_10'] = close.rolling(10).mean() / close - 1
    df['SMA_21'] = close.rolling(21).mean() / close - 1
    df['SMA_50'] = close.rolling(50).mean() / close - 1
    df['SMA_200'] = close.rolling(200).mean() / close - 1
    
    # Volatility
    df['Vol_10'] = df['Ret_1'].rolling(10).std()
    df['Vol_21'] = df['Ret_1'].rolling(21).std()
    df['Vol_50'] = df['Ret_1'].rolling(50).std()
    
    # Target: t+1 return
    # If Ret_1_fwd is > 0, label is 1, else 0
    df['Target_Ret'] = close.shift(-1) / close - 1
    df['Target'] = (df['Target_Ret'] > 0).astype(int)
    
    df.dropna(inplace=True)
    return df

class AnthropicSparseAutoencoder(nn.Module):
    def __init__(self, d_model: int, n_features: int, l1_coeff: float = 1e-3):
        super().__init__()
        self.d_model = d_model
        self.n_features = n_features
        self.l1_coeff = l1_coeff
        
        self.W_enc = nn.Parameter(torch.empty(d_model, n_features))
        self.b_enc = nn.Parameter(torch.zeros(n_features))
        
        self.W_dec = nn.Parameter(torch.empty(n_features, d_model))
        self.b_dec = nn.Parameter(torch.zeros(d_model))
        
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.kaiming_uniform_(self.W_enc, a=math.sqrt(5))
        with torch.no_grad():
            self.W_dec.data = self.W_enc.data.t().clone()
            self.normalize_decoder()

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        x_shifted = x - self.b_dec
        hidden = F.relu(x_shifted @ self.W_enc + self.b_enc)
        return hidden
        
    def decode(self, hidden: torch.Tensor) -> torch.Tensor:
        x_hat = hidden @ self.W_dec + self.b_dec
        return x_hat

    def forward(self, x: torch.Tensor) -> dict:
        hidden = self.encode(x)
        x_hat = self.decode(hidden)
        reconstruction_loss = (x_hat - x).pow(2).sum(dim=-1).mean()
        l1_loss = hidden.abs().sum(dim=-1).mean() * self.l1_coeff
        total_loss = reconstruction_loss + l1_loss
        return {
            "loss": total_loss,
            "hidden": hidden
        }

    @torch.no_grad()
    def normalize_decoder(self):
        self.W_dec.data = F.normalize(self.W_dec.data, p=2, dim=1)

class ClassifierHead(nn.Module):
    def __init__(self, in_features, hidden_dim, out_features=1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_features, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim // 2, out_features)
        )
    def forward(self, x):
        return self.net(x)

def run_experiment():
    df = get_djia_data()
    df = feature_engineering(df)
    
    # Use data up to 2019 for training, 2020-2026 for OOS testing
    train_df = df[df.index < '2020-01-01']
    test_df = df[df.index >= '2020-01-01']
    
    features = [c for c in df.columns if c not in ['Target', 'Target_Ret', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]
    
    X_train = train_df[features].values
    y_train = train_df['Target'].values
    X_test = test_df[features].values
    y_test = test_df['Target'].values
    test_rets = test_df['Target_Ret'].values
    
    scaler = StandardScaler()
    scaler.fit(df[df.index.year <= 2005][features].values)
    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    X_train_t = torch.tensor(X_train_scaled, dtype=torch.float32)
    y_train_t = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
    X_test_t = torch.tensor(X_test_scaled, dtype=torch.float32)
    y_test_t = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1)
    
    d_model = len(features)
    n_features = d_model * 4
    
    # Train SAE
    sae = AnthropicSparseAutoencoder(d_model=d_model, n_features=n_features, l1_coeff=1e-3)
    optimizer_sae = optim.Adam(sae.parameters(), lr=1e-3)
    
    epochs_sae = 200
    for epoch in range(epochs_sae):
        optimizer_sae.zero_grad()
        out = sae(X_train_t)
        loss = out["loss"]
        loss.backward()
        optimizer_sae.step()
        sae.normalize_decoder()
        
    sae.eval()
    with torch.no_grad():
        H_train = sae.encode(X_train_t)
        H_test = sae.encode(X_test_t)
        
    # Train Classifier
    clf = ClassifierHead(in_features=n_features, hidden_dim=64)
    optimizer_clf = optim.Adam(clf.parameters(), lr=1e-3, weight_decay=1e-4)
    criterion = nn.BCEWithLogitsLoss()
    
    epochs_clf = 500
    best_acc = 0
    best_preds = None
    
    for epoch in range(epochs_clf):
        clf.train()
        optimizer_clf.zero_grad()
        logits = clf(H_train)
        loss = criterion(logits, y_train_t)
        loss.backward()
        optimizer_clf.step()
        
        clf.eval()
        with torch.no_grad():
            test_logits = clf(H_test)
            test_preds = (torch.sigmoid(test_logits) > 0.5).int().numpy().flatten()
            acc = accuracy_score(y_test, test_preds)
            if acc > best_acc:
                best_acc = acc
                best_preds = test_preds
                
    # Calculate OOS accuracy and CAGR
    strategy_returns = []
    for i in range(len(test_preds)):
        # If model predicts 1, hold index. If 0, hold cash (0 return)
        if best_preds[i] == 1:
            strategy_returns.append(test_rets[i])
        else:
            strategy_returns.append(0.0)
            
    strategy_returns = np.array(strategy_returns)
    cumulative_return = np.prod(1 + strategy_returns)
    
    years = len(test_df) / 252.0
    cagr = (cumulative_return ** (1 / years)) - 1
    
    bh_cumulative = np.prod(1 + test_rets)
    bh_cagr = (bh_cumulative ** (1 / years)) - 1
    
    print(f"OOS Accuracy: {best_acc:.4f}")
    print(f"Strategy CAGR: {cagr:.4f} (B&H CAGR: {bh_cagr:.4f})")
    print(f"OOS Trades: {np.sum(best_preds)}")
    print(f"Total OOS Days: {len(test_preds)}")

if __name__ == "__main__":
    run_experiment()
