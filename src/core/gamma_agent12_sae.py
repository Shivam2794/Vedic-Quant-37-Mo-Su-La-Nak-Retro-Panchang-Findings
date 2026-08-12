import math
import torch
import torch.nn as nn
import torch.nn.functional as F

class AnthropicSparseAutoencoder(nn.Module):
    """
    Anthropic-style Sparse Autoencoder (SAE) for L1 Regularized Dictionary Learning.
    
    This architecture is commonly used to extract interpretable, monosemantic features
    from language model activations.
    
    Key features:
    - Pre-encoder bias tied to the decoder bias: f(x) = ReLU(W_enc(x - b_dec) + b_enc)
    - Decoder weights constrained to unit L2 norm to prevent scaling degenerate solutions.
    - L1 regularization on the hidden activations to encourage sparsity.
    """
    def __init__(self, d_model: int, n_features: int, l1_coeff: float = 1e-3):
        """
        Args:
            d_model (int): Dimension of the input activations.
            n_features (int): Number of features in the dictionary (typically d_model * expansion_factor).
            l1_coeff (float): Coefficient for the L1 regularization term.
        """
        super().__init__()
        self.d_model = d_model
        self.n_features = n_features
        self.l1_coeff = l1_coeff
        
        # Encoder parameters
        self.W_enc = nn.Parameter(torch.empty(d_model, n_features))
        self.b_enc = nn.Parameter(torch.zeros(n_features))
        
        # Decoder parameters
        self.W_dec = nn.Parameter(torch.empty(n_features, d_model))
        # Decoder bias, used to shift input before encoding and added back after decoding
        self.b_dec = nn.Parameter(torch.zeros(d_model))
        
        self.reset_parameters()

    def reset_parameters(self):
        """
        Initializes the parameters.
        Decoder weights are initialized as the transpose of the encoder weights and normalized.
        """
        nn.init.kaiming_uniform_(self.W_enc, a=math.sqrt(5))
        
        with torch.no_grad():
            self.W_dec.data = self.W_enc.data.t().clone()
            self.normalize_decoder()

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """
        Encodes the input activation to the sparse feature representation.
        
        Args:
            x: Input tensor of shape (batch_size, ..., d_model)
            
        Returns:
            hidden: Sparse feature activations of shape (batch_size, ..., n_features)
        """
        # Shift by decoder bias before encoding (Anthropic style)
        x_shifted = x - self.b_dec
        hidden = F.relu(x_shifted @ self.W_enc + self.b_enc)
        return hidden
        
    def decode(self, hidden: torch.Tensor) -> torch.Tensor:
        """
        Decodes the sparse features back to the original activation space.
        
        Args:
            hidden: Sparse feature activations of shape (batch_size, ..., n_features)
            
        Returns:
            x_hat: Reconstructed activations of shape (batch_size, ..., d_model)
        """
        x_hat = hidden @ self.W_dec + self.b_dec
        return x_hat

    def forward(self, x: torch.Tensor) -> dict:
        """
        Performs a forward pass computing the reconstruction and loss.
        
        Args:
            x: Input tensor of shape (batch_size, ..., d_model)
            
        Returns:
            Dictionary containing the total loss, individual loss components, and outputs.
        """
        hidden = self.encode(x)
        x_hat = self.decode(hidden)
        
        # Calculate losses
        # L2 reconstruction loss: sum over d_model, mean over batch
        reconstruction_loss = (x_hat - x).pow(2).sum(dim=-1).mean()
        
        # L1 sparsity loss: sum over n_features, mean over batch
        l1_loss = hidden.abs().sum(dim=-1).mean() * self.l1_coeff
        
        total_loss = reconstruction_loss + l1_loss
        
        return {
            "loss": total_loss,
            "reconstruction_loss": reconstruction_loss,
            "l1_loss": l1_loss,
            "x_hat": x_hat,
            "hidden": hidden
        }

    @torch.no_grad()
    def normalize_decoder(self):
        """
        Normalizes the decoder weights to have unit L2 norm along the d_model dimension.
        
        IMPORTANT: This must be called after every optimizer step!
        It prevents the model from artificially decreasing the L1 penalty by 
        scaling up the decoder weights and scaling down the encoder weights.
        """
        self.W_dec.data = F.normalize(self.W_dec.data, p=2, dim=1)


# Example usage:
if __name__ == '__main__':
    # Hyperparameters
    d_model = 512
    expansion_factor = 4
    n_features = d_model * expansion_factor
    batch_size = 32
    
    # Initialize the SAE
    sae = AnthropicSparseAutoencoder(d_model=d_model, n_features=n_features, l1_coeff=1e-3)
    
    # Dummy activations (e.g., from an LLM layer)
    activations = torch.randn(batch_size, d_model)
    
    # Optimizer
    optimizer = torch.optim.Adam(sae.parameters(), lr=1e-3)
    
    # Forward pass
    outputs = sae(activations)
    
    # Backward pass and optimization
    optimizer.zero_grad()
    outputs["loss"].backward()
    optimizer.step()
    
    # Post-step normalization (Crucial for Anthropic-style SAEs)
    sae.normalize_decoder()
    
    print(f"Total Loss: {outputs['loss'].item():.4f}")
    print(f"Reconstruction Loss: {outputs['reconstruction_loss'].item():.4f}")
    print(f"L1 Loss: {outputs['l1_loss'].item():.4f}")
    print("Decoder normalized successfully.")
