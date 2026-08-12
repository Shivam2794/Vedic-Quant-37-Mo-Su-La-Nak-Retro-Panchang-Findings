"""
Phase 6D: Macro Asset FNO Engine
================================
Trains a Fourier Neural Operator (FNO) on the Mundane Astrology 
features for SPY, QQQ, Gold, Silver, and Copper.

Allows for Long AND Short trades based on model output.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import pandas as pd
import numpy as np
import os
import glob
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit

MACRO_FEATURES_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\macro_features_partitioned"
SEQ_LEN = 21  # 21 trading days lookback (1 month)

class SpectralConv1d(nn.Module):
    def __init__(self, in_channels, out_channels, modes1):
        super(SpectralConv1d, self).__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.modes1 = modes1
        self.scale = (1 / (in_channels * out_channels))
        self.weights1 = nn.Parameter(self.scale * torch.rand(in_channels, out_channels, self.modes1, dtype=torch.cfloat))

    def compl_mul1d(self, input, weights):
        return torch.einsum("bix,iox->box", input, weights)

    def forward(self, x):
        batchsize = x.shape[0]
        x_ft = torch.fft.rfft(x)
        out_ft = torch.zeros(batchsize, self.out_channels, x.size(-1)//2 + 1,  device=x.device, dtype=torch.cfloat)
        out_ft[:, :, :self.modes1] = self.compl_mul1d(x_ft[:, :, :self.modes1], self.weights1)
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
        x = self.fc0(x)
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

def calculate_sharpe(returns, risk_free_rate=0.0):
    if len(returns) == 0 or np.std(returns) == 0: return 0.0
    daily_sharpe = (np.mean(returns) - risk_free_rate) / np.std(returns)
    return daily_sharpe * np.sqrt(252)

def train_macro_fno(ticker, target_horizon='fwd_return_21d'):
    print(f"\n{'-'*50}")
    print(f"Training FNO for {ticker} | Target: {target_horizon}")
    print(f"{'-'*50}")
    
    # Load data for ticker
    search_path = os.path.join(MACRO_FEATURES_DIR, f"ticker={ticker}", "**", "*.parquet")
    files = glob.glob(search_path, recursive=True)
    if not files:
        print(f"No data found for {ticker}")
        return
        
    df = pd.concat([pd.read_parquet(f) for f in files])
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    # Select continuous Mundane features
    exclude = ['date', 'ticker', 'open', 'high', 'low', 'close', 'volume', 'year', 'fwd_return_1d', 'fwd_return_5d', 'fwd_return_10d', 'fwd_return_21d', 'fwd_return_63d']
    features = [c for c in df.columns if c not in exclude]
    
    X_raw = df[features].values
    y_raw = df[target_horizon].values
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)
    
    # Time Series Split
    tscv = TimeSeriesSplit(n_splits=3)
    fold_metrics = []
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    for fold, (train_index, test_index) in enumerate(tscv.split(X_scaled)):
        if len(train_index) < SEQ_LEN * 2 or len(test_index) < SEQ_LEN:
            continue
            
        X_train, y_train = X_scaled[train_index], y_raw[train_index]
        X_test, y_test = X_scaled[test_index], y_raw[test_index]
        
        train_dataset = TimeSeriesDataset(X_train, y_train, SEQ_LEN)
        test_dataset = TimeSeriesDataset(X_test, y_test, SEQ_LEN)
        
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=False)
        test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
        
        modes = min(SEQ_LEN // 2, 8) 
        model = FNO1d(num_features=len(features), modes=modes, width=32).to(device)
        optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-4)
        criterion = nn.MSELoss()
        
        for ep in range(15):
            model.train()
            for seq, tgt in train_loader:
                seq, tgt = seq.to(device), tgt.to(device)
                optimizer.zero_grad()
                pred = model(seq)
                loss = criterion(pred, tgt)
                loss.backward()
                optimizer.step()
                
        model.eval()
        predictions, actuals = [], []
        with torch.no_grad():
            for seq, tgt in test_loader:
                seq = seq.to(device)
                pred = model(seq)
                predictions.extend(pred.cpu().numpy())
                actuals.extend(tgt.numpy())
                
        predictions = np.array(predictions)
        actuals = np.array(actuals)
        
        # Long/Short Strategy Evaluation
        signals = np.where(predictions > 0.005, 1, np.where(predictions < -0.005, -1, 0))
        
        # Trade returns: return * signal
        strategy_returns = actuals * signals
        strategy_returns = strategy_returns[signals != 0] # Filter out 0 signals
        
        # Calculate days for Sharpe
        horizon_days = int(target_horizon.split('_')[-1].replace('d', ''))
        
        if len(strategy_returns) > 0:
            daily_returns = strategy_returns / float(horizon_days)
            sharpe = calculate_sharpe(daily_returns)
            win_rate = np.mean(strategy_returns > 0)
        else:
            sharpe = 0.0
            win_rate = 0.0
            
        fold_metrics.append((sharpe, win_rate, len(strategy_returns), len(actuals)))
        print(f"  Fold {fold+1}: Trades={len(strategy_returns)}/{len(actuals)} | WinRate={win_rate:.1%} | Sharpe={sharpe:.2f}")

    avg_sharpe = np.mean([m[0] for m in fold_metrics])
    avg_win_rate = np.mean([m[1] for m in fold_metrics])
    
    print(f"  --> MEAN SHARPE: {avg_sharpe:.2f} | MEAN WIN RATE: {avg_win_rate:.1%}")

if __name__ == "__main__":
    print("="*60)
    print("PHASE 6D: MACRO FNO EVALUATION (MUNDANE ASTROLOGY)")
    print("="*60)
    for ticker in ['SPY', 'QQQ', 'XAUUSD', 'XAGUSD', 'COPPER']:
        train_macro_fno(ticker, 'fwd_return_10d')
