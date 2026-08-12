import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import os

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

def find_optimal_latent_dim(X_train_tensor, max_dim=12):
    dims = [2, 4, 6, 8, 10, 12, 14, 16]
    losses = []
    for dim in dims:
        model = DenoisingAutoencoder(input_dim=X_train_tensor.shape[1], latent_dim=dim, dropout_rate=0.2).double()
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=0.01)
        dataset = torch.utils.data.TensorDataset(X_train_tensor, X_train_tensor)
        loader = torch.utils.data.DataLoader(dataset, batch_size=256, shuffle=True, drop_last=False)
        model.train()
        for epoch in range(20): # fast train for eval
            for batch_x, batch_y in loader:
                optimizer.zero_grad()
                out = model(batch_x)
                loss = criterion(out, batch_y)
                loss.backward()
                optimizer.step()
        model.eval()
        with torch.no_grad():
            final_loss = criterion(model(X_train_tensor), X_train_tensor).item()
        losses.append(final_loss)
        
    # Calculate second derivative to find the elbow
    losses_array = np.array(losses)
    second_deriv = np.diff(losses_array, 2)
    elbow_idx = np.argmax(second_deriv) + 1 # +1 because diff reduces length by 2, and elbow is at the middle point
    best_dim = dims[elbow_idx]
    print(f"[INFO] Elbow method selected latent_dim={best_dim} (Losses: {losses})")
    return best_dim

def walk_forward_latent_extraction(df: pd.DataFrame, feature_cols: list, init_train_size=1000, step_size=252, epochs=50) -> pd.DataFrame:
    print(f"[INFO] Executing Walk-Forward Denoising Autoencoder (No Lookahead Leakage)...")
    
    n_samples = len(df)
    latent_df = df.copy()
    
    # Wait to initialize latent columns until after elbow method is run on first chunk
        
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
        train_end = current_idx
        test_end = min(current_idx + step_size, n_samples)
        
        X_train = df_scaled.iloc[:train_end][feature_cols].values
        X_test = df_scaled.iloc[train_end:test_end][feature_cols].values
        X_tensor = torch.tensor(X_train, dtype=torch.float64)
        
        if first_run:
            latent_dim = find_optimal_latent_dim(X_tensor)
            # Initialize latent columns with NaN now that we know the dim
            for i in range(latent_dim):
                latent_df[f'Latent_{i}'] = np.nan

        dataset = torch.utils.data.TensorDataset(X_tensor, X_tensor)
        loader = torch.utils.data.DataLoader(dataset, batch_size=256, shuffle=True, drop_last=True)
        
        model = DenoisingAutoencoder(input_dim=len(feature_cols), latent_dim=latent_dim, dropout_rate=0.2)
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=1e-3)
        
        model.train()
        for epoch in range(epochs):
            for batch_x, batch_y in loader:
                optimizer.zero_grad()
                out = model(batch_x)
                loss = criterion(out, batch_y)
                loss.backward()
                optimizer.step()
                
        if first_run:
            first_run = False
                
        # Extract latent for TEST SET (OOS)
        X_test_tensor = torch.tensor(X_test, dtype=torch.float64)
        latent_test = model.get_latent(X_test_tensor).numpy()
        
        # We also need to extract latent for TRAIN SET on the final run if we want full history, 
        # but to be strictly walk-forward, we only store OOS inferences.
        for i in range(latent_dim):
            latent_df.iloc[train_end:test_end, latent_df.columns.get_loc(f'Latent_{i}')] = latent_test[:, i]
            
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
    parser.add_argument("--ticker", type=str, required=True)
    args = parser.parse_args()
    
    ticker = args.ticker
    print(f"Executing V17 Latent Encoder Phase for {ticker} (Strict Walk-Forward)...")
    
    df = pd.read_parquet(f'{ticker}_daily_V17_raw.parquet')
    
    feature_cols = [c for c in df.columns if c not in ['Open', 'High', 'Low', 'Close', 'Volume']]
    
    df_latent = walk_forward_latent_extraction(df, feature_cols)
    out_file = f'{ticker}_daily_V17_latent.parquet'
    df_latent.to_parquet(out_file)
    print(f"[SUCCESS] Latent Market States extracted and saved to {out_file}")
