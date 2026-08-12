import torch
from torch.utils.data import DataLoader, TensorDataset
import sys
import gc
sys.path.append(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline")
from chapter5.sae_training import SparseAutoencoder, train_sae

def test_leak():
    input_dim = 64
    hidden_dim = 256
    model = SparseAutoencoder(input_dim, hidden_dim)
    
    data = torch.randn(1000, input_dim)
    dataset = TensorDataset(data)
    dataloader = DataLoader(dataset, batch_size=32)
    
    # Run once to warm up
    train_sae(model, dataloader, epochs=1, device="cpu", log_interval=100)
    
    gc.collect()
    tensors_before = len([obj for obj in gc.get_objects() if isinstance(obj, torch.Tensor)])
    
    train_sae(model, dataloader, epochs=5, device="cpu", log_interval=100)
    
    gc.collect()
    tensors_after = len([obj for obj in gc.get_objects() if isinstance(obj, torch.Tensor)])
    
    print(f"Tensors before: {tensors_before}")
    print(f"Tensors after: {tensors_after}")
    
    if tensors_after > tensors_before + 10: # Allow small threshold
        print("LEAK DETECTED!")
        sys.exit(1)
    else:
        print("NO LEAK DETECTED.")
        sys.exit(0)

if __name__ == "__main__":
    test_leak()
