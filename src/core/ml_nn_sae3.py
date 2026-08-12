import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb

# 1. Generate Dummy Data
print("Generating data...")
X, y = make_classification(n_samples=2000, n_features=1013, n_informative=100, n_classes=2, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Convert to PyTorch tensors
X_train_tensor = torch.FloatTensor(X_train)
X_test_tensor = torch.FloatTensor(X_test)

# 2. Build SAE (Sparse Autoencoder)
class SparseAutoencoder(nn.Module):
    def __init__(self, input_dim=1013, hidden_dim=512):
        super(SparseAutoencoder, self).__init__()
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

sae = SparseAutoencoder(input_dim=1013, hidden_dim=512)
criterion = nn.MSELoss()
optimizer = optim.Adam(sae.parameters(), lr=1e-3)
l1_lambda = 1e-4

# 3. Train SAE for 5 Epochs
print("Training SAE...")
epochs = 5
batch_size = 64

for epoch in range(epochs):
    epoch_loss = 0
    permutation = torch.randperm(X_train_tensor.size()[0])
    
    for i in range(0, X_train_tensor.size()[0], batch_size):
        indices = permutation[i:i+batch_size]
        batch_x = X_train_tensor[indices]
        
        optimizer.zero_grad()
        encoded, decoded = sae(batch_x)
        
        mse_loss = criterion(decoded, batch_x)
        l1_loss = torch.norm(encoded, 1)
        loss = mse_loss + l1_lambda * l1_loss
        
        loss.backward()
        optimizer.step()
        
        epoch_loss += loss.item()
        
    print(f"Epoch {epoch+1}/{epochs}, Loss: {epoch_loss / (X_train_tensor.size()[0] / batch_size):.4f}")

# 4. Freeze and Extract Latents
print("Extracting latents...")
sae.eval()
with torch.no_grad():
    latents_train, _ = sae(X_train_tensor)
    latents_test, _ = sae(X_test_tensor)

X_train_latent = latents_train.numpy()
X_test_latent = latents_test.numpy()

# 5. Train XGBoost Classifier
print("Training XGBoost...")
xgb_clf = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
xgb_clf.fit(X_train_latent, y_train)

# 6. Evaluate
print("Evaluating Classifier...")
y_pred = xgb_clf.predict(X_test_latent)
acc = accuracy_score(y_test, y_pred)
print(f"Accuracy: {acc:.4f}")
print("Classification Report:")
print(classification_report(y_test, y_pred))
