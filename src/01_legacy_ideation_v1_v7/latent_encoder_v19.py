import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import os
import yfinance as yf

class DenoisingAutoencoder(nn.Module):
    def __init__(self, input_dim, latent_dim=8, dropout_rate=0.2):
        super(DenoisingAutoencoder, self).__init__()
        self.dropout = nn.Dropout(p=dropout_rate)
        
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.BatchNorm1d(32),
            nn.LeakyReLU(0.2),
            nn.Linear(32, 16),
            nn.BatchNorm1d(16),
            nn.LeakyReLU(0.2),
            nn.Linear(16, latent_dim)
        )
        
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 16),
            nn.BatchNorm1d(16),
            nn.LeakyReLU(0.2),
            nn.Linear(16, 32),
            nn.BatchNorm1d(32),
            nn.LeakyReLU(0.2),
            nn.Linear(32, input_dim)
        )
        self.double()
        
    def forward(self, x):
        x_noisy = self.dropout(x)
        latent = self.encoder(x_noisy)
        reconstructed = self.decoder(latent)
        return reconstructed
        
    def get_latent(self, x):
        with torch.no_grad():
            self.eval()
            return self.encoder(x)

def train_autoencoder(model, X_train_tensor, epochs=50):
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    dataset = torch.utils.data.TensorDataset(X_train_tensor, X_train_tensor)
    loader = torch.utils.data.DataLoader(dataset, batch_size=256, shuffle=True, drop_last=False)
    
    model.train()
    for epoch in range(epochs):
        for batch_x, batch_y in loader:
            optimizer.zero_grad()
            out = model(batch_x)
            loss = criterion(out, batch_y)
            loss.backward()
            optimizer.step()

def get_latent_features(model, X_tensor):
    model.eval()
    with torch.no_grad():
        return model.get_latent(X_tensor).numpy()

def walk_forward_latent_extraction(df: pd.DataFrame, feature_cols: list, init_train_size=1000, step_size=252) -> pd.DataFrame:
    print(f"[INFO] Executing Rolling Walk-Forward Denoising Autoencoder (No Lookahead Leakage)...")
    
    n_samples = len(df)
    latent_df = df.copy()
    
    # We must roll standard scale to prevent global mean leakage
    df_scaled = pd.DataFrame(index=df.index)
    for col in feature_cols:
        if col.endswith('_Z'):
            df_scaled[col] = df[col]
        else:
            # Use 252-day rolling mean/std to scale inputs strictly backward looking
            roll_mean = df[col].rolling(252, min_periods=63).mean()
            roll_std = df[col].rolling(252, min_periods=63).std()
            df_scaled[col] = (df[col] - roll_mean) / np.clip(roll_std, 1e-8, None)
        
    df_scaled = df_scaled.fillna(0) # For early rows
    
    current_idx = init_train_size
    first_run = True
    latent_dim = None
    
    while current_idx < n_samples:
        train_start = max(0, current_idx - init_train_size)  # STRICT ROLLING WINDOW
        train_end = current_idx
        test_end = min(current_idx + step_size, n_samples)
        
        X_train = df_scaled.iloc[train_start:train_end][feature_cols].values
        X_test = df_scaled.iloc[train_end:test_end][feature_cols].values
        X_tensor = torch.tensor(X_train, dtype=torch.float64)
        
        # Determine latent dimension dynamically on first run (explain 95% variance)
        if first_run:
            u, s, v = torch.svd(X_tensor)
            var_explained = torch.cumsum(s**2, dim=0) / torch.sum(s**2)
            latent_dim = torch.where(var_explained > 0.95)[0][0].item() + 1
            latent_dim = max(2, min(latent_dim, len(feature_cols) // 2))
            first_run = False
            
        model = DenoisingAutoencoder(input_dim=len(feature_cols), latent_dim=latent_dim)
        train_autoencoder(model, X_tensor, epochs=50)
        
        X_test_tensor = torch.tensor(X_test, dtype=torch.float64)
        latent_features = get_latent_features(model, X_test_tensor)
        
        for i in range(latent_dim):
            col_name = f'Latent_{i}'
            if col_name not in latent_df.columns:
                latent_df[col_name] = np.nan
            latent_df.iloc[train_end:test_end, latent_df.columns.get_loc(col_name)] = latent_features[:, i]
            
        print(f"[INFO] Processed OOS chunk {train_end} to {test_end}")
        current_idx += step_size
        
    # Finally, rolling Z-score the latent features so they are standardized for Optuna
    for i in range(latent_dim):
        col = f'Latent_{i}'
        rmean = latent_df[col].rolling(252, min_periods=63).mean()
        rstd = latent_df[col].rolling(252, min_periods=63).std()
        latent_df[col] = (latent_df[col] - rmean) / np.clip(rstd, 1e-8, None)
        
    return latent_df.dropna()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", type=str, default="SPY")
    args = parser.parse_args()
    
    ticker = args.ticker
    print(f"Executing V19 Latent Encoder Phase for {ticker} (Strict Walk-Forward Rolling)...")
    
    try:
        df = pd.read_parquet(f'{ticker}_daily_V17_raw.parquet')
    except:
        print("Raw data not found, downloading...")
        df = yf.download(ticker, start="2000-01-01", end="2026-01-01")
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
        df = df[['Close', 'High', 'Low', 'Open', 'Volume']].copy()
        df['Returns'] = df['Close'].pct_change()
        df['Log_Ret'] = np.log(df['Close'] / df['Close'].shift(1))
        df['RSI_14'] = 50 # dummy for raw if missing
    
    feature_cols = [c for c in df.columns if c not in ['Open', 'High', 'Low', 'Close', 'Volume']]
    
    df_latent = walk_forward_latent_extraction(df, feature_cols)
    out_file = f'{ticker}_daily_V19_latent.parquet'
    df_latent.to_parquet(out_file)
    print(f"[SUCCESS] Latent Market States extracted and saved to {out_file}")
