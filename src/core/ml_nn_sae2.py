import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import xgboost as xgb
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import time

def main():
    # 1. Create synthetic data
    print("Generating synthetic dataset with 1013 features...")
    X, y = make_classification(n_samples=2500, n_features=1013, n_informative=100, n_redundant=50, n_classes=2, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    X_train_t = torch.tensor(X_train, dtype=torch.float32)
    X_test_t = torch.tensor(X_test, dtype=torch.float32)

    # 2. Define Sparse Autoencoder
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

    # 3. Train SAE
    input_dim = 1013
    latent_dim = 4096
    model = SAE(input_dim, latent_dim)

    # Move to GPU if available
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    X_train_t = X_train_t.to(device)
    X_test_t = X_test_t.to(device)

    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    l1_lambda = 1e-4

    epochs = 5
    batch_size = 128

    print(f"Training SAE for {epochs} epochs on {device}...")
    start_time = time.time()
    for epoch in range(epochs):
        model.train()
        permutation = torch.randperm(X_train_t.size()[0])
        epoch_loss = 0.0
        for i in range(0, X_train_t.size()[0], batch_size):
            indices = permutation[i:i+batch_size]
            batch_x = X_train_t[indices]
            
            optimizer.zero_grad()
            recon, latent = model(batch_x)
            
            mse_loss = criterion(recon, batch_x)
            l1_loss = l1_lambda * torch.norm(latent, 1) / batch_size
            
            loss = mse_loss + l1_loss
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item() * batch_x.size(0)
        print(f"Epoch {epoch+1}/{epochs}, Loss: {epoch_loss / X_train_t.size()[0]:.4f}")
    print(f"SAE Training completed in {time.time() - start_time:.2f} seconds.")

    # 4. Extract Latents
    print("Freezing SAE and extracting latents...")
    model.eval()
    with torch.no_grad():
        _, train_latents = model(X_train_t)
        _, test_latents = model(X_test_t)
        
    train_latents_np = train_latents.cpu().numpy()
    test_latents_np = test_latents.cpu().numpy()

    print(f"Latent shape: {train_latents_np.shape}")

    # 5. Train XGBoost on Latents
    print("Training XGBoost Classifier on 4096 latent dimensions...")
    start_time = time.time()
    xgb_model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        use_label_encoder=False,
        eval_metric='logloss',
        random_state=42
    )
    xgb_model.fit(train_latents_np, y_train)
    print(f"XGBoost Training completed in {time.time() - start_time:.2f} seconds.")

    # 6. Evaluate
    print("Evaluating model...")
    y_pred = xgb_model.predict(test_latents_np)
    acc = accuracy_score(y_test, y_pred)

    print("-" * 30)
    print("Results:")
    print(f"Accuracy: {acc:.4f}")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    print("-" * 30)

if __name__ == '__main__':
    main()
