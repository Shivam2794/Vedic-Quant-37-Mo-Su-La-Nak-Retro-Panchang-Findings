import pandas as pd
import numpy as np
import torch
from torch import nn, optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def main():
    file_path = r"C:\Users\Shivam Patel\.gemini\antigravity\data_lake\orion_batch_DJIA_PUBLICATION_enriched.parquet"
    
    try:
        df = pd.read_parquet(file_path)
    except FileNotFoundError:
        print(f"Error: Could not find file at {file_path}")
        return
    
    # Identify year, target, and return columns based on typical naming conventions
    year_col = 'Year' if 'Year' in df.columns else [c for c in df.columns if 'year' in c.lower()][0]
    
    # Try to find a target column
    target_cols = [c for c in df.columns if 'target' in c.lower() or 'label' in c.lower()]
    if not target_cols:
        print("Could not identify a target column. Available columns:", df.columns.tolist()[:10])
        return
    target_col = target_cols[0]
    
    # Try to find a return column for CAGR/Drawdown
    return_cols = [c for c in df.columns if 'return' in c.lower()]
    if not return_cols:
        print("Could not identify a return column. Using target as fallback for metrics.")
        return_col = target_col
    else:
        return_col = return_cols[0]

    exclude_cols = {target_col, return_col, year_col, 'Date', 'Ticker', 'index'}
    features = [c for c in df.columns if c not in exclude_cols]
    
    # Use 1013 features as specified
    if len(features) > 1013:
        features = features[:1013]
    elif len(features) < 1013:
        print(f"Warning: Only found {len(features)} features, requested 1013.")

    # Split dataset
    train_mask = df[year_col] <= 2005
    test_mask = df[year_col] >= 2006
    
    X_train = df.loc[train_mask, features].fillna(0).values
    y_train = df.loc[train_mask, target_col].values
    
    X_test = df.loc[test_mask, features].fillna(0).values
    y_test = df.loc[test_mask, target_col].values
    returns_test = df.loc[test_mask, return_col].fillna(0).values

    # Clean target for classification (ensure integers)
    y_train = np.where(y_train > 0, 1, 0)
    y_test = np.where(y_test > 0, 1, 0)

    # ----------------------------------------------------
    # SAE Definition
    # ----------------------------------------------------
    class SparseAutoencoder(nn.Module):
        def __init__(self, input_dim, hidden_dim):
            super().__init__()
            self.encoder = nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU()
            )
            self.decoder = nn.Linear(hidden_dim, input_dim)
            
        def forward(self, x):
            latent = self.encoder(x)
            reconstructed = self.decoder(latent)
            return reconstructed, latent

    input_dim = X_train.shape[1]
    hidden_dim = 512
    sae = SparseAutoencoder(input_dim, hidden_dim)

    criterion = nn.MSELoss()
    optimizer = optim.Adam(sae.parameters(), lr=1e-3)
    l1_lambda = 1e-5

    X_train_tensor = torch.FloatTensor(X_train)
    dataset = TensorDataset(X_train_tensor)
    dataloader = DataLoader(dataset, batch_size=256, shuffle=True)

    # ----------------------------------------------------
    # Train SAE for 10 epochs
    # ----------------------------------------------------
    epochs = 10
    print("Training SAE...")
    for epoch in range(epochs):
        epoch_loss = 0
        for batch_x, in dataloader:
            optimizer.zero_grad()
            reconstructed, latent = sae(batch_x)
            mse_loss = criterion(reconstructed, batch_x)
            l1_loss = l1_lambda * torch.norm(latent, 1)
            loss = mse_loss + l1_loss
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
            
    # ----------------------------------------------------
    # Extract Latents
    # ----------------------------------------------------
    sae.eval()
    with torch.no_grad():
        _, train_latents = sae(torch.FloatTensor(X_train))
        _, test_latents = sae(torch.FloatTensor(X_test))
        
    train_latents = train_latents.numpy()
    test_latents = test_latents.numpy()

    # ----------------------------------------------------
    # Train Random Forest
    # ----------------------------------------------------
    print("Training Random Forest...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(train_latents, y_train)

    # ----------------------------------------------------
    # Predict on Year >= 2006 and Metrics
    # ----------------------------------------------------
    preds = rf.predict(test_latents)
    accuracy = accuracy_score(y_test, preds)

    # Strategy: assuming 1 = long, 0 = no position
    strategy_returns = preds * returns_test
    
    # CAGR calculation (assuming approx 252 trading days per year)
    cum_ret = (1 + strategy_returns).prod()
    years = len(strategy_returns) / 252.0
    cagr = cum_ret ** (1 / years) - 1 if years > 0 else 0

    # Max Drawdown calculation
    cum_returns_series = pd.Series(strategy_returns).add(1).cumprod()
    peaks = cum_returns_series.cummax()
    drawdown = (cum_returns_series - peaks) / peaks
    max_drawdown = drawdown.min()

    print("\n--- RESULTS ---")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"CAGR: {cagr:.4f}")
    print(f"Max Drawdown: {max_drawdown:.4f}")

if __name__ == "__main__":
    main()
