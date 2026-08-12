import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

class SparseAutoencoder(nn.Module):
    def __init__(self, input_dim=1013, latent_dim=2048):
        super(SparseAutoencoder, self).__init__()
        self.encoder = nn.Linear(input_dim, latent_dim)
        self.relu = nn.ReLU()
        self.decoder = nn.Linear(latent_dim, input_dim)

    def forward(self, x):
        latents = self.relu(self.encoder(x))
        reconstructed = self.decoder(latents)
        return reconstructed, latents

def train_sae(model, dataloader, epochs=5, l1_lambda=1e-5, lr=1e-3):
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    model.train()
    for epoch in range(epochs):
        epoch_loss = 0.0
        for batch in dataloader:
            x = batch[0]
            optimizer.zero_grad()
            
            reconstructed, latents = model(x)
            
            mse_loss = criterion(reconstructed, x)
            # L1 penalty on the latent activations
            l1_loss = l1_lambda * torch.mean(torch.abs(latents))
            loss = mse_loss + l1_loss
            
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            
        print(f"Epoch {epoch+1}/{epochs}, Loss: {epoch_loss/len(dataloader):.4f}")

def main():
    # 1. Generate synthetic data
    print("Generating synthetic data...")
    num_samples = 2000
    input_dim = 1013
    latent_dim = 2048
    
    # Random normal features
    X = torch.randn(num_samples, input_dim)
    # Synthetic returns target (binary classification)
    y = torch.randint(0, 2, (num_samples,)).numpy()
    
    dataset = torch.utils.data.TensorDataset(X)
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=64, shuffle=True)
    
    # 2. Initialize and train SAE
    print("Initializing Sparse Autoencoder...")
    sae = SparseAutoencoder(input_dim=input_dim, latent_dim=latent_dim)
    
    print("Training SAE for 5 epochs...")
    train_sae(sae, dataloader, epochs=5, l1_lambda=1e-4)
    
    # 3. Freeze SAE and extract latents
    print("Extracting latents...")
    sae.eval()
    with torch.no_grad():
        _, latents = sae(X)
        X_latents = latents.numpy()
        
    # 4. Train Logistic Regression
    print("Training Logistic Regression classifier on latents...")
    X_train, X_test, y_train, y_test = train_test_split(X_latents, y, test_size=0.2, random_state=42)
    
    clf = LogisticRegression(max_iter=1000)
    clf.fit(X_train, y_train)
    
    # 5. Predict and report results
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print("\n--- Results ---")
    print(f"Accuracy: {acc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

if __name__ == "__main__":
    main()
