import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import os

class ExtremeVarianceDataset(Dataset):
    def __init__(self, num_samples, seq_len):
        self.num_samples = num_samples
        self.seq_len = seq_len
        self.data = []
        self.targets = []
        for _ in range(num_samples):
            is_extreme = torch.rand(1).item() > 0.5
            if not is_extreme:
                # Normal variance
                seq = torch.randn(seq_len, 1)
            else:
                # Extreme variance
                seq = torch.randn(seq_len, 1) * 10.0
                
            self.data.append(seq)
            self.targets.append(torch.tensor([1.0 if is_extreme else 0.0]))
            
    def __len__(self):
        return self.num_samples
    
    def __getitem__(self, idx):
        return self.data[idx], self.targets[idx]

class SimpleTransformer(nn.Module):
    def __init__(self, input_dim, embed_dim, num_heads):
        super().__init__()
        self.embedding = nn.Linear(input_dim, embed_dim)
        self.attention = nn.MultiheadAttention(embed_dim, num_heads, batch_first=True)
        self.fc = nn.Linear(embed_dim, 1)
        
    def forward(self, x):
        x = self.embedding(x)
        # Self-attention
        attn_out, attn_weights = self.attention(x, x, x, need_weights=True)
        # Pool across sequence length
        pooled = attn_out.mean(dim=1)
        out = self.fc(pooled)
        return out, attn_weights

def main():
    torch.manual_seed(42)
    seq_len = 10
    dataset = ExtremeVarianceDataset(1000, seq_len)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    model = SimpleTransformer(input_dim=1, embed_dim=16, num_heads=2)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    
    print("Training started...")
    for epoch in range(10):
        total_loss = 0
        for batch_x, batch_y in dataloader:
            optimizer.zero_grad()
            pred, _ = model(batch_x)
            loss = criterion(pred, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1}, Loss: {total_loss / len(dataloader):.4f}")
        
    print("Training completed.")
    
    # Extract final trained Attention
    sample_x, sample_y = dataset[0]
    sample_x = sample_x.unsqueeze(0) # batch size 1
    model.eval()
    with torch.no_grad():
        _, attn_weights = model(sample_x)
    
    print("Final trained Attention weights shape:", attn_weights.shape)
    print("Attention weights for first sample:\n", attn_weights[0])
    
    # Save attention weights
    output_path = os.path.join(os.path.dirname(__file__), "final_attention_weights.pt")
    torch.save(attn_weights, output_path)
    print(f"Saved final attention weights to {output_path}")

if __name__ == "__main__":
    main()
