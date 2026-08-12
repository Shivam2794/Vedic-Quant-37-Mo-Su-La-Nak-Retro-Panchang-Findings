import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import xgboost as xgb
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
import traceback

def main():
    print("Loading data...")
    path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\data_lake\orion_batch_DJIA_PUBLICATION_enriched"
    df = pd.read_parquet(path)
    
    print("Data loaded. Shape:", df.shape)
    
    # Identify Year
    year_col = 'Year'
    if year_col not in df.columns:
        date_cols = [c for c in df.columns if 'date' in c.lower()]
        if date_cols:
            df['Year'] = pd.to_datetime(df[date_cols[0]]).dt.year
        else:
            print("Columns:", df.columns.tolist())
            raise ValueError("No Year or Date column found")

    date_cols = [c for c in df.columns if 'date' in c.lower()]
    date_col = date_cols[0] if date_cols else None
            
    # Target
    target_cols = [c for c in df.columns if c.lower() in ['target', 'label', 'y'] or 'target' in c.lower()]
    if target_cols:
        target_col = target_cols[0]
    else:
        print("Columns:", df.columns.tolist())
        raise ValueError("No target column found")
        
    print(f"Target column selected: {target_col}")

    # Returns
    return_cols = [c for c in df.columns if ('return' in c.lower() or 'ret' in c.lower() or 'fwd' in c.lower()) and c != target_col]
    ret_col = return_cols[0] if return_cols else None
    print(f"Return column selected: {ret_col}")

    # Features
    exclude_cols = [year_col, target_col, ret_col, 'Date', 'date', 'Symbol', 'ticker', 'asset'] + date_cols
    features = [c for c in df.columns if c not in exclude_cols]
    
    if len(features) != 1013:
        print(f"Warning: Found {len(features)} features, expected 1013.")
        features = [c for c in features if pd.api.types.is_numeric_dtype(df[c])]
        print(f"Numeric features count: {len(features)}")
                
    print(f"Using {len(features)} features.")
    
    # Mask
    train_mask = df['Year'] <= 2005
    test_mask = df['Year'] >= 2006
    
    X_train = df.loc[train_mask, features].fillna(0).values
    y_train = df.loc[train_mask, target_col].values
    X_test = df.loc[test_mask, features].fillna(0).values
    y_test = df.loc[test_mask, target_col].values
    
    # Convert continuous target to binary if needed
    if len(np.unique(y_train)) > 10:
        print("Target appears continuous. Converting to binary (y > 0).")
        y_train = (y_train > 0).astype(int)
        y_test = (y_test > 0).astype(int)
    else:
        # Convert -1/1 to 0/1 for xgboost if necessary, XGBoost prefers 0,1,2...
        if -1 in y_train:
            print("Converting -1/1 labels to 0/1 for XGBoost.")
            y_train = np.where(y_train == 1, 1, 0)
            y_test = np.where(y_test == 1, 1, 0)
    
    # Scale
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    class SparseAutoencoder(nn.Module):
        def __init__(self, input_dim, hidden_dim, sparsity_weight=1e-3):
            super().__init__()
            self.encoder = nn.Linear(input_dim, hidden_dim)
            self.relu = nn.ReLU()
            self.decoder = nn.Linear(hidden_dim, input_dim)
            self.sparsity_weight = sparsity_weight

        def forward(self, x):
            encoded = self.relu(self.encoder(x))
            decoded = self.decoder(encoded)
            return encoded, decoded

        def loss_function(self, decoded, x, encoded):
            mse_loss = nn.MSELoss()(decoded, x)
            l1_loss = torch.mean(torch.abs(encoded))
            return mse_loss + self.sparsity_weight * l1_loss

    input_dim = X_train.shape[1]
    model = SparseAutoencoder(input_dim=input_dim, hidden_dim=4096)
    
    # Use GPU if available
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    model.to(device)
    
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    
    X_train_t = torch.FloatTensor(X_train).to(device)
    dataset = TensorDataset(X_train_t)
    dataloader = DataLoader(dataset, batch_size=256, shuffle=True)
    
    print("Training SAE...")
    for epoch in range(10):
        model.train()
        total_loss = 0
        for batch in dataloader:
            x_batch = batch[0]
            optimizer.zero_grad()
            encoded, decoded = model(x_batch)
            loss = model.loss_function(decoded, x_batch, encoded)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1}, Loss: {total_loss/len(dataloader):.4f}")
        
    print("Extracting latents...")
    model.eval()
    with torch.no_grad():
        X_test_t = torch.FloatTensor(X_test).to(device)
        train_latents, _ = model(X_train_t)
        test_latents, _ = model(X_test_t)
        
    train_latents = train_latents.cpu().numpy()
    test_latents = test_latents.cpu().numpy()
    
    print("Training XGBoost...")
    clf = xgb.XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.1, random_state=42)
    clf.fit(train_latents, y_train)
    
    print("Predicting...")
    preds = clf.predict(test_latents)
    
    acc = accuracy_score(y_test, preds)
    print(f"Accuracy: {acc:.4f}")
    
    # CAGR and Drawdown
    if ret_col is not None and date_col is not None:
        ret_test = df.loc[test_mask, ret_col].fillna(0).values
        # Signal mapping: 1 if pred==1 else -1
        signal = np.where(preds > 0, 1, -1)
        
        results = pd.DataFrame({
            'Date': df.loc[test_mask, date_col],
            'Signal': signal,
            'Return': ret_test
        })
        
        daily_strat_ret = results.groupby('Date').apply(lambda x: (x['Signal'] * x['Return']).mean())
        
        cum_ret = np.prod(1 + daily_strat_ret)
        n_years = len(daily_strat_ret) / 252.0
        if n_years > 0:
            cagr = (cum_ret ** (1 / n_years)) - 1
        else:
            cagr = 0.0
            
        cum_returns = np.cumprod(1 + daily_strat_ret)
        running_max = np.maximum.accumulate(cum_returns)
        drawdowns = (cum_returns - running_max) / running_max
        max_drawdown = np.min(drawdowns)
        
        print(f"CAGR: {cagr:.4f}")
        print(f"Drawdown: {max_drawdown:.4f}")
    else:
        print("Return or Date column not available for CAGR/Drawdown calculation.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error encountered:")
        traceback.print_exc()
