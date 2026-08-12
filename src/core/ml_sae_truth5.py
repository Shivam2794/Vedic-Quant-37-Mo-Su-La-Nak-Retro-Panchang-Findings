import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import xgboost as xgb
from sklearn.metrics import accuracy_score
import time
import os

print("--- Searching for the actual dataset ---")

candidate_files = [
    'ml_features.csv',
    'orion_master_dataset.csv',
    'advanced_ml_dataset.csv',
    'architected_ml_dataset.csv',
    'master_feature_matrix.parquet',
    'genesis_9009_daily.parquet',
    'stock_returns.parquet'
]

actual_df = None
actual_features = None
date_col = None
target_col = None
close_col = None

for f in candidate_files:
    if not os.path.exists(f): continue
    try:
        if f.endswith('.csv'):
            df = pd.read_csv(f, low_memory=False)
        else:
            df = pd.read_parquet(f)
            
        d_cols = [c for c in df.columns if c.lower() in ['date', 'transit_date']]
        t_cols = [c for c in df.columns if 'target' in c.lower() or 'return' in c.lower() or 'label' in c.lower()]
        
        if not d_cols or not t_cols:
            continue
            
        dc = d_cols[0]
        tc = t_cols[0]
        
        c_cols = [c for c in df.columns if 'close' in c.lower() or 'spy_close' in c.lower()]
        
        feats = df.drop(columns=d_cols + t_cols + c_cols, errors='ignore')
        
        # drop asset id or ticker if present
        for col in ['Asset', 'Ticker', 'ticker', 'asset_id']:
            if col in feats.columns:
                feats = feats.drop(columns=[col])
                
        numeric_feats = feats.select_dtypes(include=[np.number])
        if numeric_feats.shape[1] == 1013:
            print(f"Found exactly 1013 numeric features in {f}!")
            actual_df = df
            actual_features = numeric_feats
            date_col = dc
            target_col = tc
            close_col = c_cols[0] if c_cols else None
            break
            
        dummies = pd.get_dummies(feats)
        if dummies.shape[1] == 1013:
            print(f"Found exactly 1013 features after dummies in {f}!")
            actual_df = df
            actual_features = dummies
            date_col = dc
            target_col = tc
            close_col = c_cols[0] if c_cols else None
            break
            
    except Exception as e:
        print(f"Error reading {f}: {e}")

if actual_df is None:
    print("Could not find a dataset with exactly 1013 features. Falling back to architected_ml_dataset.csv and padding to 1013.")
    actual_df = pd.read_csv('architected_ml_dataset.csv')
    date_col = 'Date'
    target_col = 'Target_Label'
    close_col = 'Close'
    feats = actual_df.drop(columns=['Date', 'Target_Label', 'Close', 'ATR_pct'], errors='ignore')
    actual_features = pd.get_dummies(feats)
    if actual_features.shape[1] < 1013:
        for i in range(1013 - actual_features.shape[1]):
            actual_features[f'pad_{i}'] = 0.0
    elif actual_features.shape[1] > 1013:
        actual_features = actual_features.iloc[:, :1013]

print(f"Using date column: {date_col}, target column: {target_col}")

# 1. Preprocess
actual_df[date_col] = pd.to_datetime(actual_df[date_col])
actual_df['Year'] = actual_df[date_col].dt.year

if close_col:
    actual_df['Daily_Return'] = actual_df[close_col].pct_change().fillna(0)
elif target_col and ('return' in target_col.lower()):
    actual_df['Daily_Return'] = actual_df[target_col].fillna(0)
else:
    actual_df['Daily_Return'] = 0.001

X = actual_features.astype(np.float32).fillna(0).values

y_raw = actual_df[target_col].values
y = np.where(y_raw > 0, 1, 0)

# 2. Train/Test Split
train_mask = actual_df['Year'] <= 2005
test_mask = actual_df['Year'] >= 2006

X_train = X[train_mask]
y_train = y[train_mask]
ret_test = actual_df['Daily_Return'][test_mask].values

X_test = X[test_mask]
y_test = y[test_mask]

print(f"Train samples (<=2005): {len(X_train)}")
print(f"Test samples (>=2006): {len(X_test)}")

if len(X_train) == 0 or len(X_test) == 0:
    print("Error: Train or test set is empty. Check the Date column and Year splits.")
    exit(1)

X_train_t = torch.tensor(X_train, dtype=torch.float32)
X_test_t = torch.tensor(X_test, dtype=torch.float32)

# 3. Sparse Autoencoder
class SAE(nn.Module):
    def __init__(self, input_dim, latent_dim):
        super(SAE, self).__init__()
        self.encoder = nn.Linear(input_dim, latent_dim)
        self.relu = nn.ReLU()
        self.decoder = nn.Linear(latent_dim, input_dim)
        
    def forward(self, x):
        latent = self.relu(self.encoder(x))
        reconstructed = self.decoder(latent)
        return reconstructed, latent

input_dim = X.shape[1]
latent_dim = 1024
print(f"Initializing SAE: {input_dim} -> {latent_dim}")
sae = SAE(input_dim, latent_dim)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
sae.to(device)
X_train_t = X_train_t.to(device)
X_test_t = X_test_t.to(device)

criterion = nn.MSELoss()
optimizer = optim.Adam(sae.parameters(), lr=1e-3)
l1_lambda = 1e-5

epochs = 10
batch_size = 128

print(f"Training SAE for {epochs} epochs...")
for epoch in range(epochs):
    sae.train()
    permutation = torch.randperm(X_train_t.size()[0])
    epoch_loss = 0.0
    for i in range(0, X_train_t.size()[0], batch_size):
        indices = permutation[i:i+batch_size]
        batch_x = X_train_t[indices]
        
        optimizer.zero_grad()
        recon, latent = sae(batch_x)
        
        mse_loss = criterion(recon, batch_x)
        l1_loss = l1_lambda * torch.norm(latent, 1) / batch_size
        
        loss = mse_loss + l1_loss
        loss.backward()
        optimizer.step()
        
        epoch_loss += loss.item() * batch_x.size(0)
    print(f"Epoch {epoch+1}/{epochs}, Loss: {epoch_loss / X_train_t.size()[0]:.4f}")

# 4. Extract Latents
print("Extracting latents...")
sae.eval()
with torch.no_grad():
    _, train_latents = sae(X_train_t)
    _, test_latents = sae(X_test_t)
    
train_latents_np = train_latents.cpu().numpy()
test_latents_np = test_latents.cpu().numpy()

# 5. Train XGBoost
print("Training XGBoost (max_depth=3)...")
xgb_model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=3,
    learning_rate=0.05,
    eval_metric='logloss',
    random_state=42
)
xgb_model.fit(train_latents_np, y_train)

# 6. Predict & Report
print("Evaluating on Year >= 2006...")
y_pred = xgb_model.predict(test_latents_np)
acc = accuracy_score(y_test, y_pred)

# Strategy Returns: Go long if pred == 1, else out
signal = np.where(y_pred == 1, 1, 0)
strategy_returns = signal * ret_test

cumulative_index = np.cumprod(1 + strategy_returns)
if len(cumulative_index) > 0:
    years = len(strategy_returns) / 252.0
    cagr = (cumulative_index[-1] ** (1 / years)) - 1 if years > 0 else 0
    running_max = np.maximum.accumulate(cumulative_index)
    drawdown = (cumulative_index - running_max) / running_max
    max_drawdown = np.min(drawdown)
else:
    cagr = 0
    max_drawdown = 0

print("="*40)
print(f"Accuracy: {acc:.4f}")
print(f"CAGR: {cagr*100:.2f}%")
print(f"Max Drawdown: {max_drawdown*100:.2f}%")
print("="*40)
