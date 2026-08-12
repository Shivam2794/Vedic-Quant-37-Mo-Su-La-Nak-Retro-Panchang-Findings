"""
Phase 0 / Step 0.3: FAISS Semantic Deduplication
=================================================
Uses the 1024-dim bge-m3 embeddings already stored in the VDB files
to find near-duplicate entities (cosine sim > 0.92) and merge them.

Input:  vedic_knowledge.db (19,327 entities)
Output: Updated vedic_knowledge.db with dedup_cluster_id column
        + dedup_stats in stats table
"""
import json
import os
import base64
import sqlite3
import numpy as np
import faiss
from collections import defaultdict

# ─── Paths ───
BASE = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\d3e7ccf9-35e0-46db-bcc3-2a44cc32acd1\scratch\vedic_graphs"
DB_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\vedic_knowledge.db"
COSINE_THRESHOLD = 0.92  # Entities with sim > 0.92 are considered duplicates

def load_embeddings(vdb_path):
    """Load the embedding matrix from a VDB file."""
    with open(vdb_path, encoding="utf-8") as f:
        vdb = json.load(f)

    emb_dim = vdb["embedding_dim"]
    decoded = base64.b64decode(vdb["matrix"])
    mat = np.frombuffer(decoded, dtype=np.float32).reshape(-1, emb_dim).copy()
    names = [d["entity_name"] for d in vdb["data"]]
    return mat, names, emb_dim

def find_duplicate_clusters(matrix, names, threshold=0.92):
    """Use FAISS to find clusters of near-duplicate embeddings."""
    n, d = matrix.shape
    print(f"  Building FAISS index for {n} vectors of dim {d}...")

    # L2-normalize (should already be, but ensure)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1
    matrix_normed = matrix / norms

    # Inner product search (= cosine sim on normalized vectors)
    index = faiss.IndexFlatIP(d)
    index.add(matrix_normed.astype(np.float32))

    # Search for k nearest neighbors
    k = min(20, n)  # Check top-20 neighbors
    similarities, indices = index.search(matrix_normed.astype(np.float32), k)

    # Build clusters via Union-Find
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    # Connect entities that exceed threshold
    merge_count = 0
    for i in range(n):
        for j_idx in range(1, k):  # Skip self (index 0)
            j = indices[i][j_idx]
            sim = similarities[i][j_idx]
            if sim >= threshold and i != j:
                union(i, j)
                merge_count += 1

    # Extract clusters
    clusters = defaultdict(list)
    for i in range(n):
        root = find(i)
        clusters[root].append(i)

    # Identify representative for each cluster (longest description wins)
    return clusters, merge_count

def main():
    print("=" * 60)
    print("PHASE 0.3: FAISS Semantic Deduplication")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Add dedup columns if not exist
    try:
        c.execute("ALTER TABLE entities ADD COLUMN dedup_cluster_id INTEGER")
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        c.execute("ALTER TABLE entities ADD COLUMN is_cluster_rep BOOLEAN DEFAULT 1")
    except sqlite3.OperationalError:
        pass

    # ─── Load embeddings from both VDB files ───
    print("\nLoading Nadi embeddings...")
    nadi_mat, nadi_names, emb_dim = load_embeddings(
        os.path.join(BASE, "nadi_sutras_memory", "vdb_entities.json"))
    print(f"  Loaded {nadi_mat.shape[0]} Nadi vectors")

    print("Loading Jaimini embeddings...")
    jaim_mat, jaim_names, _ = load_embeddings(
        os.path.join(BASE, "jaimini_memory", "vdb_entities.json"))
    print(f"  Loaded {jaim_mat.shape[0]} Jaimini vectors")

    # ─── Combine into single matrix ───
    all_matrix = np.vstack([nadi_mat, jaim_mat])
    all_names = nadi_names + jaim_names
    all_sources = ["nadi"] * len(nadi_names) + ["jaimini"] * len(jaim_names)
    print(f"\nCombined matrix: {all_matrix.shape}")

    # ─── Find clusters ───
    print(f"\nFinding duplicates (cosine sim > {COSINE_THRESHOLD})...")
    clusters, merge_count = find_duplicate_clusters(all_matrix, all_names, COSINE_THRESHOLD)

    # ─── Analyze results ───
    multi_clusters = {k: v for k, v in clusters.items() if len(v) > 1}
    singleton_count = sum(1 for v in clusters.values() if len(v) == 1)
    total_merged = sum(len(v) for v in multi_clusters.values())

    print(f"\n  Total entities: {len(all_names)}")
    print(f"  Unique clusters: {len(clusters)}")
    print(f"  Singletons (unique): {singleton_count}")
    print(f"  Multi-entity clusters: {len(multi_clusters)}")
    print(f"  Entities in multi-clusters: {total_merged}")
    print(f"  Effective unique count: {len(clusters)}")
    print(f"  Reduction: {len(all_names)} -> {len(clusters)} ({100*(1-len(clusters)/len(all_names)):.1f}% eliminated)")

    # ─── Show sample clusters ───
    print(f"\n  SAMPLE DUPLICATE CLUSTERS (top 15 by size):")
    sorted_clusters = sorted(multi_clusters.items(), key=lambda x: len(x[1]), reverse=True)
    for cluster_id, member_indices in sorted_clusters[:15]:
        rep_name = all_names[member_indices[0]]
        member_names = [all_names[i] for i in member_indices]
        print(f"\n    Cluster (size={len(member_indices)}): Representative = '{rep_name}'")
        for mn in member_names[:5]:
            src = all_sources[member_indices[member_names.index(mn)]]
            print(f"      [{src:7s}] {mn[:80]}")
        if len(member_names) > 5:
            print(f"      ... and {len(member_names)-5} more")

    # ─── Update SQLite ───
    print("\nUpdating database with cluster assignments...")
    cluster_id_counter = 0
    for root_idx, member_indices in clusters.items():
        cluster_id_counter += 1
        # Pick representative: prefer longer description
        descs = []
        for idx in member_indices:
            name = all_names[idx]
            source = all_sources[idx]
            row = c.execute(
                "SELECT id, length(description) FROM entities WHERE entity_name = ? AND source = ?",
                (name, source)
            ).fetchone()
            if row:
                descs.append((row[0], row[1] or 0, idx))

        if not descs:
            continue

        # Representative = entity with longest description
        descs.sort(key=lambda x: x[1], reverse=True)
        rep_db_id = descs[0][0]

        for db_id, _, _ in descs:
            is_rep = 1 if db_id == rep_db_id else 0
            c.execute(
                "UPDATE entities SET dedup_cluster_id = ?, is_cluster_rep = ? WHERE id = ?",
                (cluster_id_counter, is_rep, db_id)
            )

    # ─── Store stats ───
    c.execute("INSERT OR REPLACE INTO stats (key, value) VALUES ('dedup_total_entities', ?)", (str(len(all_names)),))
    c.execute("INSERT OR REPLACE INTO stats (key, value) VALUES ('dedup_unique_clusters', ?)", (str(len(clusters)),))
    c.execute("INSERT OR REPLACE INTO stats (key, value) VALUES ('dedup_multi_clusters', ?)", (str(len(multi_clusters)),))
    c.execute("INSERT OR REPLACE INTO stats (key, value) VALUES ('dedup_singletons', ?)", (str(singleton_count),))
    c.execute("INSERT OR REPLACE INTO stats (key, value) VALUES ('dedup_threshold', ?)", (str(COSINE_THRESHOLD),))

    conn.commit()

    # ─── Final summary ───
    rep_count = c.execute("SELECT COUNT(*) FROM entities WHERE is_cluster_rep = 1").fetchone()[0]
    comp_rep = c.execute("SELECT COUNT(*) FROM entities WHERE is_cluster_rep = 1 AND is_computable = 1").fetchone()[0]

    print(f"\n{'='*60}")
    print(f"DEDUP COMPLETE")
    print(f"{'='*60}")
    print(f"  Cluster representatives: {rep_count}")
    print(f"  Computable representatives: {comp_rep}")
    print(f"  Original -> Deduped: {len(all_names)} -> {rep_count}")

    # Category breakdown of representatives
    print(f"\n  DEDUPED CATEGORY BREAKDOWN:")
    for row in c.execute("""
        SELECT category, COUNT(*) as cnt
        FROM entities WHERE is_cluster_rep = 1
        GROUP BY category ORDER BY cnt DESC
    """):
        print(f"    {row[0]:25s} {row[1]:5d}")

    conn.close()
    print(f"\nDatabase updated: {DB_PATH}")

if __name__ == "__main__":
    main()
