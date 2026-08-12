import torch
import torch.nn as nn

class StructuredSelfAttentionPooling(nn.Module):
    """
    Multi-head self-attention pooling layer, based on Lin et al. (2017) 
    'A Structured Self-attentive Sentence Embedding'.
    
    This layer computes multiple attention distributions over the sequence length,
    allowing the model to focus on different aspects/features of the sequence.
    The resulting context vectors for each head are concatenated.
    """
    def __init__(self, input_dim: int, num_heads: int, hidden_dim: int = None):
        super().__init__()
        self.input_dim = input_dim
        self.num_heads = num_heads
        
        if hidden_dim is None:
            hidden_dim = input_dim
            
        # 2-layer MLP to compute attention weights for multiple heads
        self.attention = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, num_heads)
        )
        
    def forward(self, x: torch.Tensor, mask: torch.Tensor = None) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            x (torch.Tensor): Input sequence tensor of shape (batch_size, seq_len, input_dim).
            mask (torch.Tensor, optional): Boolean padding mask of shape (batch_size, seq_len).
                                           True indicates padding tokens to be ignored.
        Returns:
            torch.Tensor: Pooled representation of shape (batch_size, num_heads * input_dim).
            torch.Tensor: Attention weights of shape (batch_size, num_heads, seq_len).
        """
        # Calculate attention logits
        # Shape: (batch_size, seq_len, num_heads)
        attn_logits = self.attention(x)
        
        # Apply padding mask if provided
        if mask is not None:
            # Expand mask to match logits shape: (batch_size, seq_len, 1)
            # Fill masked positions with -inf so they receive 0 probability after softmax
            attn_logits = attn_logits.masked_fill(mask.unsqueeze(-1), float('-inf'))
            
        # Normalize along the sequence dimension
        # Shape: (batch_size, seq_len, num_heads)
        attn_weights = torch.softmax(attn_logits, dim=1)
        
        # Multiply input sequence by attention weights
        # x: (batch_size, seq_len, input_dim)
        # attn_weights transposed: (batch_size, num_heads, seq_len)
        # Output pooled: (batch_size, num_heads, input_dim)
        pooled = torch.bmm(attn_weights.transpose(1, 2), x)
        
        # Flatten the head and input dimensions
        # Shape: (batch_size, num_heads * input_dim)
        pooled_flat = pooled.view(x.size(0), -1)
        
        return pooled_flat, attn_weights


class QueryBasedMultiHeadAttentionPooling(nn.Module):
    """
    Multi-head attention pooling layer using learnable query (seed) vectors.
    Similar to Pooling by Multihead Attention (PMA) from the Set Transformer architecture.
    """
    def __init__(self, embed_dim: int, num_heads: int, num_queries: int = 1, dropout: float = 0.1):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.num_queries = num_queries
        
        # Learnable queries (seed vectors)
        self.queries = nn.Parameter(torch.empty(1, num_queries, embed_dim))
        nn.init.xavier_uniform_(self.queries)
        
        self.mha = nn.MultiheadAttention(
            embed_dim=embed_dim, 
            num_heads=num_heads, 
            dropout=dropout, 
            batch_first=True
        )
        
        self.layer_norm = nn.LayerNorm(embed_dim)
        
        # Feed-Forward Network following the attention block
        self.ffn = nn.Sequential(
            nn.Linear(embed_dim, embed_dim * 4),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(embed_dim * 4, embed_dim),
            nn.Dropout(dropout)
        )
        self.layer_norm_ffn = nn.LayerNorm(embed_dim)

    def forward(self, x: torch.Tensor, padding_mask: torch.Tensor = None) -> torch.Tensor:
        """
        Args:
            x (torch.Tensor): Input sequence tensor of shape (batch_size, seq_len, embed_dim).
            padding_mask (torch.Tensor, optional): Boolean padding mask of shape (batch_size, seq_len).
                                                   True indicates padding tokens.
        Returns:
            torch.Tensor: Pooled representation. 
                          Shape is (batch_size, num_queries, embed_dim).
                          If num_queries == 1, it is squeezed to (batch_size, embed_dim).
        """
        batch_size = x.size(0)
        
        # Expand the learnable queries to match the batch size
        # Shape: (batch_size, num_queries, embed_dim)
        batch_queries = self.queries.expand(batch_size, -1, -1)
        
        # Multi-head attention (Queries: learnable, Keys/Values: input sequence)
        attn_out, _ = self.mha(
            query=batch_queries,
            key=x,
            value=x,
            key_padding_mask=padding_mask
        )
        
        # Residual connection and layer normalization
        out = self.layer_norm(batch_queries + attn_out)
        
        # FFN with residual connection and layer normalization
        ffn_out = self.ffn(out)
        out = self.layer_norm_ffn(out + ffn_out)
        
        # Squeeze the query dimension if there's only a single query token
        if self.num_queries == 1:
            out = out.squeeze(1)
            
        return out


# Example Usage & Testing
if __name__ == "__main__":
    batch_size = 4
    seq_len = 16
    embed_dim = 64
    num_heads = 4
    
    # Dummy input and mask
    x = torch.randn(batch_size, seq_len, embed_dim)
    mask = torch.zeros(batch_size, seq_len, dtype=torch.bool)
    mask[:, -2:] = True  # Mask out the last two elements as padding
    
    print("Testing StructuredSelfAttentionPooling...")
    model1 = StructuredSelfAttentionPooling(input_dim=embed_dim, num_heads=num_heads)
    out1, weights1 = model1(x, mask=mask)
    print(f"Input shape: {x.shape}")
    print(f"Output shape: {out1.shape}")
    print(f"Weights shape: {weights1.shape}")
    
    print("\nTesting QueryBasedMultiHeadAttentionPooling (Single Query)...")
    model2 = QueryBasedMultiHeadAttentionPooling(embed_dim=embed_dim, num_heads=num_heads, num_queries=1)
    out2 = model2(x, padding_mask=mask)
    print(f"Output shape: {out2.shape}")

    print("\nTesting QueryBasedMultiHeadAttentionPooling (Multi Query)...")
    model3 = QueryBasedMultiHeadAttentionPooling(embed_dim=embed_dim, num_heads=num_heads, num_queries=3)
    out3 = model3(x, padding_mask=mask)
    print(f"Output shape: {out3.shape}")
