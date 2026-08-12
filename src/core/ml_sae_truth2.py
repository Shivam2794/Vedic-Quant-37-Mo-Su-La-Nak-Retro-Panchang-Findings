import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler

def main():
    file_path = r'C:\Users\Shivam Patel\.gemini\antigravity\data_lake\orion_batch_DJIA_PUBLICATION_enriched.parquet'
    print(f"Loading data from {file_path}...")
    try:
        df = pd.read_parquet(file_path)
    except Exception as e:
        print(f"Error loading parquet file: {e}")
        return

    # Identify Year
    year_col = 'Year' if 'Year' in df.columns else 'year'
    if year_col not in df.columns and 'Date' in df.columns:
        df['Year'] = pd.to_datetime(df['Date']).dt.year
        year_col = 'Year'

    if year_col not in df.columns:
        print("Could not identify Year column.")
        return

    # Train / Test split
    train_df = df[df[year_col] <= 2005].copy()
    test_df = df[df[year_col] >= 2006].copy()

    # Identify target
    target_cols = ['Target', 'target', 'Label', 'label', 'Direction', 'direction']
    target_col = next((c for c in target_cols if c in df.columns), None)
    
    # Identify return
    return_cols = ['Return', 'return', 'Returns', 'returns', 'Forward_Return', 'LogReturn']
    return_col = next((c for c in return_cols if c in df.columns), None)
    
    if not target_col:
        # Fallback to creating a binary target from Returns if possible
        if return_col:
            train_df['Target'] = (train_df[return_col] > 0).astype(int)
            test_df['Target'] = (test_df[return_col] > 0).astype(int)
            target_col = 'Target'
        else:
            print("Could not identify Target column.")
            return

    if not return_col:
        print("Could not identify Returns column for CAGR/Drawdown calculation. Exiting.")
        return

    # Identify features
    exclude_cols = [year_col, target_col, return_col, 'Date', 'date']
    features = [c for c in df.columns if c not in exclude_cols]
    
    # We expect 1013 features based on the instructions
    numeric_features = df[features].select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_features) >= 1013:
        feature_cols = numeric_features[:1013]
    else:
        feature_cols = numeric_features

    print(f"Using {len(feature_cols)} features for training.")
    print(f"Train samples: {len(train_df)}, Test samples: {len(test_df)}")

    X_train = train_df[feature_cols].values
    y_train = train_df[target_col].values

    X_test = test_df[feature_cols].values
    y_test = test_df[target_col].values
    returns_test = test_df[return_col].values

    X_train = np.nan_to_num(X_train)
    X_test = np.nan_to_num(X_test)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # PyTorch SAE
    class SAE(nn.Module):
        def __init__(self, input_dim, hidden_dim):
            super().__init__()
            self.encoder = nn.Linear(input_dim, hidden_dim)
            self.relu = nn.ReLU()
            self.decoder = nn.Linear(hidden_dim, input_dim)

        def forward(self, x):
            encoded = self.relu(self.encoder(x))
            decoded = self.decoder(encoded)
            return encoded, decoded

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    model = SAE(len(feature_cols), 2048).to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)

    X_train_tensor = torch.FloatTensor(X_train_scaled).to(device)
    dataset = TensorDataset(X_train_tensor, X_train_tensor)
    loader = DataLoader(dataset, batch_size=256, shuffle=True)

    print("Training SAE...")
    model.train()
    for epoch in range(10):
        epoch_loss = 0
        for batch_x, _ in loader:
            optimizer.zero_grad()
            encoded, decoded = model(batch_x)
            loss = criterion(decoded, batch_x)
            # L1 sparsity
            l1_loss = torch.mean(torch.abs(encoded))
            total_loss = loss + 1e-3 * l1_loss
            total_loss.backward()
            optimizer.step()
            epoch_loss += total_loss.item()
        print(f"Epoch {epoch+1}/10, Loss: {epoch_loss/len(loader):.4f}")

    print("Extracting latents...")
    model.eval()
    with torch.no_grad():
        X_train_latents, _ = model(X_train_tensor)
        X_train_latents = X_train_latents.cpu().numpy()
        
        X_test_tensor = torch.FloatTensor(X_test_scaled).to(device)
        X_test_latents, _ = model(X_test_tensor)
        X_test_latents = X_test_latents.cpu().numpy()

    print("Training Logistic Regression...")
    clf = LogisticRegression(max_iter=1000)
    clf.fit(X_train_latents, y_train)

    y_pred = clf.predict(X_test_latents)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc:.4f}")

    # Calculate strategy returns
    strategy_returns = returns_test * np.where(y_pred == 1, 1, -1)
    
    cumulative_returns = np.cumprod(1 + strategy_returns)

    # CAGR
    years = len(strategy_returns) / 252 # Assuming daily data
    if years > 0:
        cagr = (cumulative_returns[-1]) ** (1 / years) - 1
    else:
        cagr = 0

    # Drawdown
    running_max = np.maximum.accumulate(cumulative_returns)
    drawdown = (cumulative_returns - running_max) / running_max
    max_drawdown = np.min(drawdown)

    print(f"CAGR: {cagr:.4%}")
    print(f"Max Drawdown: {max_drawdown:.4%}")

if __name__ == "__main__":
    main()
