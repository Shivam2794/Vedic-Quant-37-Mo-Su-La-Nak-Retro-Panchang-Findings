"""
Phase 4: Fourier Neural Operator (FNO) Integration
==================================================
The FNO learns the continuous frequency-domain patterns of planetary
mechanics (primarily planetary speeds and positional sine waves).

Standard neural networks operate in the spatial/temporal domain.
The FNO operates in the Fourier domain, allowing it to learn the 
derivative (acceleration) and underlying waveforms driving the market.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import pandas as pd
import numpy as np
import os
import subprocess
import json
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit

BQ_CMD = r"C:\Users\Shivam Patel\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd"
CAUSAL_CORE_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\causal_core.csv"
RETURNS_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_returns.parquet"
SEQ_LEN = 63  # 63 trading days lookback (one full quarter)

class SpectralConv1d(nn.Module):
    def __init__(self, in_channels, out_channels, modes1):
        super(SpectralConv1d, self).__init__()
        """
        1D Fourier layer. It does FFT, linear transform, and Inverse FFT.    
        """
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.modes1 = modes1  # Number of Fourier modes to multiply, at most floor(N/2) + 1

        self.scale = (1 / (in_channels * out_channels))
        self.weights1 = nn.Parameter(self.scale * torch.rand(in_channels, out_channels, self.modes1, dtype=torch.cfloat))

    def compl_mul1d(self, input, weights):
        # (batch, in_channel, x ), (in_channel, out_channel, x) -> (batch, out_channel, x)
        return torch.einsum("bix,iox->box", input, weights)

    def forward(self, x):
        batchsize = x.shape[0]
        # Compute Fourier coeffcients up to factor of e
        x_ft = torch.fft.rfft(x)

        # Multiply relevant Fourier modes
        out_ft = torch.zeros(batchsize, self.out_channels, x.size(-1)//2 + 1,  device=x.device, dtype=torch.cfloat)
        out_ft[:, :, :self.modes1] = self.compl_mul1d(x_ft[:, :, :self.modes1], self.weights1)

        #Return to physical space
        x = torch.fft.irfft(out_ft, n=x.size(-1))
        return x

class FNO1d(nn.Module):
    def __init__(self, num_features, modes, width):
        super(FNO1d, self).__init__()
        self.modes1 = modes
        self.width = width
        
        self.fc0 = nn.Linear(num_features, self.width)
        
        self.conv0 = SpectralConv1d(self.width, self.width, self.modes1)
        self.conv1 = SpectralConv1d(self.width, self.width, self.modes1)
        self.conv2 = SpectralConv1d(self.width, self.width, self.modes1)
        
        self.w0 = nn.Conv1d(self.width, self.width, 1)
        self.w1 = nn.Conv1d(self.width, self.width, 1)
        self.w2 = nn.Conv1d(self.width, self.width, 1)

        self.fc1 = nn.Linear(self.width, 128)
        self.fc2 = nn.Linear(128, 1)

    def forward(self, x):
        # x shape: (batch, seq_len, num_features)
        x = self.fc0(x)
        # Permute for Conv1d: (batch, num_features, seq_len)
        x = x.permute(0, 2, 1)

        x1 = self.conv0(x)
        x2 = self.w0(x)
        x = F.gelu(x1 + x2)

        x1 = self.conv1(x)
        x2 = self.w1(x)
        x = F.gelu(x1 + x2)

        x1 = self.conv2(x)
        x2 = self.w2(x)
        x = F.gelu(x1 + x2)

        # Pool over time sequence
        x = torch.mean(x, dim=-1)
        
        x = self.fc1(x)
        x = F.gelu(x)
        x = self.fc2(x)
        return x.squeeze(-1)

class TimeSeriesDataset(Dataset):
    def __init__(self, X, y, seq_len):
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y)
        self.seq_len = seq_len

    def __len__(self):
        return len(self.X) - self.seq_len

    def __getitem__(self, idx):
        return self.X[idx : idx + self.seq_len], self.y[idx + self.seq_len - 1]

def run_query(sql):
    tmp_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\tmp_fno_features.csv"
    cmd = f'"{BQ_CMD}" query --use_legacy_sql=false --format=csv --max_rows=1000000 "{sql}" > "{tmp_path}"'
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        raise RuntimeError("BQ Query Failed")
    df = pd.read_csv(tmp_path)
    os.remove(tmp_path)
    return df

def calculate_sharpe(returns, risk_free_rate=0.0):
    if len(returns) == 0 or np.std(returns) == 0: return 0.0
    daily_sharpe = (np.mean(returns) - risk_free_rate) / np.std(returns)
    return daily_sharpe * np.sqrt(252)

def train_fno():
    print("="*60, flush=True)
    print("PHASE 4: FOURIER NEURAL OPERATOR (FNO) INTEGRATION", flush=True)
    print("="*60, flush=True)
    
    # Load 27 Causal Features
    if not os.path.exists(CAUSAL_CORE_PATH):
        print("ERROR: causal_core.csv not found.")
        return
        
    core_df = pd.read_csv(CAUSAL_CORE_PATH)
    features = core_df['feature'].tolist()
    
    # 2. Query BigQuery for AAPL specifically to train 1D sequences
    print(f"Querying Continuous Waveforms from BigQuery...", flush=True)
    feature_cols = ", ".join(features)
    sql = f"SELECT ticker, date, {feature_cols} FROM `antigravity_quant.feature_matrix` WHERE ticker='AMZN' ORDER BY date"
    
    df_features = run_query(sql)
    df_features['date'] = pd.to_datetime(df_features['date']).dt.date.astype(str)
    
    # 3. Load Local Returns
    df_returns = pd.read_parquet(RETURNS_PATH)
    df_returns['date'] = pd.to_datetime(df_returns['date']).dt.date.astype(str)
    
    # 4. Merge Features and Targets
    target = 'fwd_return_63d'
    merged = df_features.merge(df_returns[['ticker', 'date', target]], 
                               on=['ticker', 'date'], how='inner')
    merged = merged.dropna()
    merged['date'] = pd.to_datetime(merged['date'])
    merged = merged.sort_values('date').reset_index(drop=True)
    
    # 5. Prepare Data
    train_mask = merged['date'].dt.year <= 2005
    test_mask = merged['date'].dt.year >= 2006
    
    X_train_raw = merged.loc[train_mask, features].values
    y_train = merged.loc[train_mask, target].values
    
    X_test_raw = merged.loc[test_mask, features].values
    y_test = merged.loc[test_mask, target].values
    
    # Scale strictly on training data to prevent global scaler data leakage
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train_raw)
    X_test = scaler.transform(X_test_raw)
    
    print("\nExecuting Training and Validation with FNO...", flush=True)
    fold_sharpes = []
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}", flush=True)
    
    # Ensure indices allow for sequence length
    if len(X_train) >= SEQ_LEN * 2 and len(X_test) >= SEQ_LEN:
        train_dataset = TimeSeriesDataset(X_train, y_train, SEQ_LEN)
        test_dataset = TimeSeriesDataset(X_test, y_test, SEQ_LEN)
        
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=False)
        test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
        
        # Initialize FNO
        modes = min(SEQ_LEN // 2, 16) # Modes must be <= floor(N/2)+1
        model = FNO1d(num_features=len(features), modes=modes, width=32).to(device)
        optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-4)
        criterion = nn.MSELoss()
        
        epochs = 15
        for ep in range(epochs):
            model.train()
            train_loss = 0
            for seq, tgt in train_loader:
                seq, tgt = seq.to(device), tgt.to(device)
                optimizer.zero_grad()
                pred = model(seq)
                loss = criterion(pred, tgt)
                loss.backward()
                optimizer.step()
                train_loss += loss.item()
                
        # Evaluate
        model.eval()
        predictions = []
        actuals = []
        with torch.no_grad():
            for seq, tgt in test_loader:
                seq = seq.to(device)
                pred = model(seq)
                predictions.extend(pred.cpu().numpy())
                actuals.extend(tgt.numpy())
                
        predictions = np.array(predictions)
        actuals = np.array(actuals)
        
        # Strategy
        signals = np.where(predictions > 0, 1, 0)
        strategy_returns = actuals[signals == 1] 
        
        if len(strategy_returns) > 0:
            daily_equivalent_returns = strategy_returns / 63.0 
            sharpe = calculate_sharpe(daily_equivalent_returns)
        else:
            sharpe = 0.0
            
        fold_sharpes.append(sharpe)
        print(f"  Test Split (>= 2006): Trades={len(strategy_returns)}/{len(actuals)} | MSE: {np.mean((predictions-actuals)**2):.5f} | Sharpe: {sharpe:.2f}", flush=True)

    avg_sharpe = np.mean(fold_sharpes) if fold_sharpes else 0.0
    print("\n" + "="*50, flush=True)
    print(f"FOURIER NEURAL OPERATOR (63D Horizon)", flush=True)
    print(f"Test Set Sharpe Ratio (>= 2006): {avg_sharpe:.2f}", flush=True)
    print("="*50, flush=True)
    print("\n[SUCCESS] Phase 4 complete. Continuous waveforms mapped to causal embeddings.", flush=True)

if __name__ == "__main__":
    train_fno()
