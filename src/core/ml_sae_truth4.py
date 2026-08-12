import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

def get_cagr(returns, periods_per_year=252):
    cum_ret = (1 + returns).prod()
    years = len(returns) / periods_per_year
    return cum_ret ** (1 / years) - 1 if years > 0 else 0.0

def get_max_drawdown(returns):
    cum_rets = (1 + returns).cumprod()
    running_max = np.maximum.accumulate(cum_rets)
    drawdowns = (cum_rets - running_max) / running_max
    return np.min(drawdowns)

def main():
    print("Loading data...")
    df = pd.read_parquet(r"C:\Users\Shivam Patel\.gemini\antigravity\data_lake\orion_batch_DJIA_PUBLICATION_enriched.parquet")
    print("Columns:", df.columns.tolist()[:10], "...", df.columns.tolist()[-10:])

    year_col = 'Year' if 'Year' in df.columns else 'year'
    
    target_col = None
    possible_targets = ['Target', 'target', 'Return', 'return', 'Returns', 'returns', 'Forward_Return', 'Label', 'label', 'Next_Return']
    for col in possible_targets:
        if col in df.columns:
            target_col = col
            break
            
    if target_col is None:
        target_col = df.columns[-1]

    print("Year column:", year_col)
    print("Target column:", target_col)

    exclude_cols = [year_col, target_col, 'Date', 'date', 'timestamp', 'Ticker', 'ticker']
    feature_cols = [c for c in df.columns if c not in exclude_cols and pd.api.types.is_numeric_dtype(df[c])]
    
    if len(feature_cols) > 1013:
        feature_cols = feature_cols[:1013]
    elif len(feature_cols) < 1013:
        print(f"Warning: Only found {len(feature_cols)} numeric feature columns, but expected at least 1013.")

    # Fill NaNs
    df[feature_cols] = df[feature_cols].fillna(0.0)
    df[target_col] = df[target_col].fillna(0.0)

    train_df = df[df[year_col] <= 2005]
    test_df = df[df[year_col] >= 2006]

    X_train = torch.tensor(train_df[feature_cols].values, dtype=torch.float32)
    y_train = torch.tensor(train_df[target_col].values, dtype=torch.float32).unsqueeze(1)
    X_test = torch.tensor(test_df[feature_cols].values, dtype=torch.float32)
    y_test = torch.tensor(test_df[target_col].values, dtype=torch.float32).unsqueeze(1)

    print("X_train shape:", X_train.shape)

    class SparseAutoencoder(nn.Module):
        def __init__(self, input_dim, hidden_dim):
            super().__init__()
            self.encoder = nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU()
            )
            self.decoder = nn.Sequential(
                nn.Linear(hidden_dim, input_dim)
            )
        def forward(self, x):
            encoded = self.encoder(x)
            decoded = self.decoder(encoded)
            return encoded, decoded

    sae = SparseAutoencoder(X_train.shape[1], 4096)
    optimizer = optim.Adam(sae.parameters(), lr=1e-3)
    criterion = nn.MSELoss()

    print("Training SAE...")
    dataset = TensorDataset(X_train)
    loader = DataLoader(dataset, batch_size=256, shuffle=True)

    l1_lambda = 1e-5
    for epoch in range(10):
        for batch_x, in loader:
            optimizer.zero_grad()
            encoded, decoded = sae(batch_x)
            loss = criterion(decoded, batch_x)
            l1_loss = l1_lambda * torch.norm(encoded, 1)
            total_loss = loss + l1_loss
            total_loss.backward()
            optimizer.step()

    print("Extracting latents...")
    with torch.no_grad():
        Z_train, _ = sae(X_train)
        Z_test, _ = sae(X_test)

    class SimpleMLP(nn.Module):
        def __init__(self, input_dim, hidden_dim, output_dim):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, output_dim)
            )
        def forward(self, x):
            return self.net(x)

    mlp = SimpleMLP(4096, 128, 1)
    mlp_optimizer = optim.Adam(mlp.parameters(), lr=1e-3)
    
    unique_targets = set(train_df[target_col].dropna().unique())
    is_classification = unique_targets.issubset({0, 1, 0.0, 1.0, -1, -1.0})
    
    if is_classification:
        # If target is -1, 1, map to 0, 1 for BCE
        if -1 in unique_targets:
            y_train_bce = (y_train > 0).float()
        else:
            y_train_bce = y_train
        mlp_criterion = nn.BCEWithLogitsLoss()
    else:
        y_train_bce = y_train
        mlp_criterion = nn.MSELoss()

    print("Training MLP...")
    mlp_dataset = TensorDataset(Z_train, y_train_bce)
    mlp_loader = DataLoader(mlp_dataset, batch_size=256, shuffle=True)

    for epoch in range(10):
        for batch_z, batch_y in mlp_loader:
            mlp_optimizer.zero_grad()
            preds = mlp(batch_z)
            loss = mlp_criterion(preds, batch_y)
            loss.backward()
            mlp_optimizer.step()

    print("Predicting...")
    with torch.no_grad():
        test_preds = mlp(Z_test)
        if is_classification:
            test_preds_labels = (torch.sigmoid(test_preds) > 0.5).float()
            # map back to -1, 1 for signals
            signals = test_preds_labels.numpy().flatten() * 2 - 1
            if -1 in unique_targets:
                acc_target = (y_test > 0).float()
            else:
                acc_target = y_test
            accuracy = (test_preds_labels == acc_target).float().mean().item()
        else:
            test_preds_labels = test_preds
            accuracy = (torch.sign(test_preds_labels) == torch.sign(y_test)).float().mean().item()
            signals = torch.sign(test_preds_labels).numpy().flatten()

    actual_returns = test_df[target_col].values
    strategy_returns = signals * actual_returns

    cagr = get_cagr(strategy_returns)
    drawdown = get_max_drawdown(strategy_returns)

    print("--------------------------------------------------")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"CAGR: {cagr:.4f}")
    print(f"Drawdown: {drawdown:.4f}")

if __name__ == "__main__":
    main()
