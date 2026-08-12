import torch
import numpy as np
from sklearn.cluster import KMeans
from typing import Tuple, List, Dict

def map_top_attention_to_clusters(
    attention_weights: torch.Tensor,
    planetary_coordinates: torch.Tensor,
    n_clusters: int = 5,
    percentile: float = 0.99
) -> Dict[str, any]:
    """
    Maps the top 1% attention weights to specific N-dimensional planetary clusters.
    
    Args:
        attention_weights: Tensor of shape (num_entities, num_entities) representing attention.
        planetary_coordinates: Tensor of shape (num_entities, n_dimensions) representing planetary features.
        n_clusters: Number of planetary clusters to form.
        percentile: The percentile threshold for attention weights (e.g., 0.99 for top 1%).
        
    Returns:
        A dictionary containing the mapping logic results.
    """
    if attention_weights.dim() != 2 or attention_weights.size(0) != attention_weights.size(1):
        raise ValueError("attention_weights must be a square 2D tensor.")
        
    num_entities = attention_weights.size(0)
    if planetary_coordinates.size(0) != num_entities:
        raise ValueError("Number of entities in coordinates must match attention weights.")
        
    # 1. Cluster the N-dimensional planetary coordinates
    coords_np = planetary_coordinates.detach().cpu().numpy()
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    cluster_labels = kmeans.fit_predict(coords_np)
    
    # 2. Find the top 1% attention weights
    # Flatten the weights to find the threshold
    flat_weights = attention_weights.flatten()
    k = max(1, int((1.0 - percentile) * flat_weights.numel()))
    
    # Get top-k values and indices
    topk_values, topk_indices = torch.topk(flat_weights, k)
    
    # 3. Map indices back to 2D
    row_indices = topk_indices // num_entities
    col_indices = topk_indices % num_entities
    
    # 4. Map attention pairs to clusters
    cluster_mappings = []
    for val, row, col in zip(topk_values, row_indices, col_indices):
        r, c = row.item(), col.item()
        cluster_mappings.append({
            'source_entity': r,
            'target_entity': c,
            'source_cluster': int(cluster_labels[r]),
            'target_cluster': int(cluster_labels[c]),
            'attention_weight': val.item()
        })
        
    # Summarize interactions between clusters
    cluster_interaction_counts = np.zeros((n_clusters, n_clusters), dtype=int)
    for mapping in cluster_mappings:
        cluster_interaction_counts[mapping['source_cluster'], mapping['target_cluster']] += 1
        
    return {
        'cluster_labels': cluster_labels.tolist(),
        'cluster_centers': kmeans.cluster_centers_.tolist(),
        'top_attention_mappings': cluster_mappings,
        'cluster_interaction_counts': cluster_interaction_counts.tolist(),
        'threshold': topk_values[-1].item()
    }

if __name__ == "__main__":
    # Example usage / Test
    num_planets = 1000
    n_dims = 3
    
    # Mock attention weights (e.g., from a Transformer model)
    # Using softmax to simulate attention distribution per row
    raw_attn = torch.randn(num_planets, num_planets)
    attn_weights = torch.softmax(raw_attn, dim=-1)
    
    # Mock N-dimensional planetary coordinates (e.g., 3D space)
    planet_coords = torch.randn(num_planets, n_dims) * 100
    
    print("Mapping top 1% attention weights to planetary clusters...")
    results = map_top_attention_to_clusters(
        attention_weights=attn_weights,
        planetary_coordinates=planet_coords,
        n_clusters=8,
        percentile=0.99
    )
    
    print(f"Number of top 1% attention links: {len(results['top_attention_mappings'])}")
    print(f"Attention threshold: {results['threshold']:.6f}")
    
    print("\nCluster Interaction Counts (Source Cluster -> Target Cluster):")
    counts = results['cluster_interaction_counts']
    for i in range(len(counts)):
        for j in range(len(counts[i])):
            if counts[i][j] > 0:
                print(f"Cluster {i} -> Cluster {j}: {counts[i][j]} links")
