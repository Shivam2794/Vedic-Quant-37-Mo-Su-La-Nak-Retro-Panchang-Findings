"""
Phase 6E: Intraday 15-Min Engine
================================
Pulls 15-min intraday OHLCV for SPY and QQQ (using yfinance recent 60-day limit),
computes 15-min continuous Mundane Astrology features, and trains a
high-frequency FNO model to predict intraday forward returns.
"""
import yfinance as yf
import pandas as pd
import numpy as np
import swisseph as swe
from datetime import timezone
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit

OUTPUT_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\intraday_features"

# FNO Architecture (Reused for 1D)
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
        self.fc0 = nn.Linear(num_features, width)
        self.conv0 = SpectralConv1d(width, width, modes)
        self.conv1 = SpectralConv1d(width, width, modes)
        self.w0 = nn.Conv1d(width, width, 1)
        self.w1 = nn.Conv1d(width, width, 1)
        self.fc1 = nn.Linear(width, 128)
        self.fc2 = nn.Linear(128, 1)

    def forward(self, x):
        x = self.fc0(x).permute(0, 2, 1)
        x = F.gelu(self.conv0(x) + self.w0(x))
        x = F.gelu(self.conv1(x) + self.w1(x))
        x = torch.mean(x, dim=-1)
        return self.fc2(F.gelu(self.fc1(x))).squeeze(-1)

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
    return daily_sharpe * np.sqrt(252 * 26) # 252 days * ~26 15-min bars/day

# Ephemeris Engine
swe.set_sid_mode(swe.SIDM_LAHIRI)
def compute_intraday_sky(dt_utc):
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60.0)
    ayanamsa = swe.get_ayanamsa(jd)
    
    features = {}
    planets = {"Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, 
               "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER, 
               "Saturn": swe.SATURN, "Uranus": swe.URANUS}
               
    for name, pid in planets.items():
        pos = swe.calc_ut(jd, pid)
        lon = (pos[0][0] - ayanamsa) % 360
        features[f"{name}_speed"] = pos[0][3]
        features[f"{name}_lon_sin"] = np.sin(np.radians(lon))
        features[f"{name}_lon_cos"] = np.cos(np.radians(lon))
    return features

def generate_intraday_data(ticker):
    print(f"Downloading 15-min data for {ticker} (Last 60 Days)...")
    df = yf.download(ticker, interval="15m", period="60d", progress=False)
    
    if len(df) == 0:
        print("No data retrieved.")
        return None
        
    df = df.reset_index()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    
    col_map = {c: c.capitalize() if c.lower() != 'datetime' else 'Datetime' for c in df.columns}
    df = df.rename(columns=col_map)
    
    # 4 bars = 1 hour, 26 bars = 1 day
    # Target: Predict next 1 hour return (4 bars)
    df['fwd_return_1h'] = df['Close'].pct_change(periods=4).shift(-4)
    df = df.dropna()
    
    print(f"Generating 15-min astronomical features for {len(df)} bars...")
    features_list = []
    for dt in df['Datetime']:
        dt_utc = dt.tz_convert('UTC') if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        features_list.append(compute_intraday_sky(dt_utc))
        
    feat_df = pd.DataFrame(features_list)
    result = pd.concat([df.reset_index(drop=True), feat_df.reset_index(drop=True)], axis=1)
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    out_path = os.path.join(OUTPUT_DIR, f"{ticker}_15m.parquet")
    result.to_parquet(out_path, index=False)
    return result

def train_intraday_fno(ticker, df):
    print(f"\n{'-'*50}")
    print(f"Training Intraday 15-Min FNO for {ticker} | Target: 1-Hour Forward")
    print(f"{'-'*50}")
    
    exclude = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'fwd_return_1h']
    features = [c for c in df.columns if c not in exclude]
    
    X_raw = df[features].values
    y_raw = df['fwd_return_1h'].values
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)
    
    tscv = TimeSeriesSplit(n_splits=3)
    fold_metrics = []
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    SEQ_LEN = 26 # Lookback 1 full day
    
    for fold, (train_index, test_index) in enumerate(tscv.split(X_scaled)):
        if len(train_index) < SEQ_LEN * 2 or len(test_index) < SEQ_LEN:
            continue
            
        X_train, y_train = X_scaled[train_index], y_raw[train_index]
        X_test, y_test = X_scaled[test_index], y_raw[test_index]
        
        train_loader = DataLoader(TimeSeriesDataset(X_train, y_train, SEQ_LEN), batch_size=64, shuffle=False)
        test_loader = DataLoader(TimeSeriesDataset(X_test, y_test, SEQ_LEN), batch_size=64, shuffle=False)
        
        modes = 8 
        model = FNO1d(num_features=len(features), modes=modes, width=32).to(device)
        optimizer = torch.optim.AdamW(model.parameters(), lr=0.001)
        criterion = nn.MSELoss()
        
        for ep in range(10):
            model.train()
            for seq, tgt in train_loader:
                optimizer.zero_grad()
                loss = criterion(model(seq.to(device)), tgt.to(device))
                loss.backward()
                optimizer.step()
                
        model.eval()
        preds, acts = [], []
        with torch.no_grad():
            for seq, tgt in test_loader:
                preds.extend(model(seq.to(device)).cpu().numpy())
                acts.extend(tgt.numpy())
                
        preds = np.array(preds)
        acts = np.array(acts)
        
        # 1-Hour Intraday Strategy: Long > 0.0005 (5 bps expected), Short < -0.0005
        signals = np.where(preds > 0.0005, 1, np.where(preds < -0.0005, -1, 0))
        strat_returns = acts[signals != 0] * signals[signals != 0]
        
        if len(strat_returns) > 0:
            sharpe = calculate_sharpe(strat_returns)
            win_rate = np.mean(strat_returns > 0)
        else:
            sharpe = 0.0; win_rate = 0.0
            
        fold_metrics.append((sharpe, win_rate, len(strat_returns), len(acts)))
        print(f"  Fold {fold+1}: Trades={len(strat_returns)}/{len(acts)} | WinRate={win_rate:.1%} | Sharpe={sharpe:.2f}")

    if fold_metrics:
        print(f"  --> MEAN SHARPE: {np.mean([m[0] for m in fold_metrics]):.2f}")

def main():
    print("=" * 60)
    print("PHASE 6E: INTRADAY 15-MIN ENGINE")
    print("=" * 60)
    for ticker in ["SPY", "QQQ"]:
        df = generate_intraday_data(ticker)
        if df is not None:
            train_intraday_fno(ticker, df)

if __name__ == "__main__":
    main()
