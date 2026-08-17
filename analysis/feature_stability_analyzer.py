import os
import glob
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from master_trading_plan_v7 import V5ContinuousVedicEngine, load_celestial_matrix

def main():
    print("[Analyzer] Starting Feature Stability Analysis...")
    
    # 1. Dynamically get feature names to avoid hallucination
    raw_df, _ = load_celestial_matrix()
    # We only need 1 row to get the column names
    engine = V5ContinuousVedicEngine(raw_df.head(10)) 
    tensor_df = engine.compute_all_tensors()
    feature_cols = [c for c in tensor_df.columns if c != 'date']
    n_features = len(feature_cols)
    print(f"[Analyzer] Extracted {n_features} continuous planetary features.")
    
    # 2. Glob all fold champions
    model_dir = "v6_fold_models"
    files = sorted(glob.glob(os.path.join(model_dir, "fold_*_champion.json")))
    n_folds = len(files)
    if n_folds == 0:
        print(f"[Analyzer] ERROR: No fold models found in {model_dir}")
        return
        
    print(f"[Analyzer] Found {n_folds} Walk-Forward OOS Fold Champions.")
    
    # 3. Aggregate weights
    activation_count = np.zeros(n_features, dtype=int)
    weight_sum = np.zeros(n_features, dtype=float)
    active_signs = {i: [] for i in range(n_features)}
    
    fold_weights_matrix = np.zeros((n_folds, n_features))
    
    for i, fpath in enumerate(files):
        with open(fpath, 'r') as f:
            data = json.load(f)
            w = np.array(data['weights'])
            v_th = data['v_th']
            
            # Re-apply L1 hard threshold pruning exactly as the physics engine does
            active_mask = np.abs(w) >= (0.05 * v_th)
            w_clean = np.where(active_mask, w, 0.0)
            
            fold_weights_matrix[i, :] = w_clean
            activation_count += active_mask.astype(int)
            weight_sum += w_clean
            
            for j in range(n_features):
                if active_mask[j]:
                    active_signs[j].append(np.sign(w_clean[j]))
                    
    # 4. Compute statistics
    results = []
    for j in range(n_features):
        act_freq = activation_count[j] / n_folds
        mean_w = (weight_sum[j] / activation_count[j]) if activation_count[j] > 0 else 0.0
        
        # Check sign consistency (e.g., if it's always positive or always negative)
        signs = active_signs[j]
        sign_consistency = 0.0
        if len(signs) > 0:
            pos = sum(1 for s in signs if s > 0)
            neg = sum(1 for s in signs if s < 0)
            sign_consistency = max(pos, neg) / len(signs)
            
        results.append({
            'Feature': feature_cols[j],
            'Activation_Freq': act_freq,
            'Total_Activations': activation_count[j],
            'Mean_Active_Weight': mean_w,
            'Sign_Consistency': sign_consistency
        })
        
    df_res = pd.DataFrame(results)
    df_res = df_res.sort_values(by=['Activation_Freq', 'Sign_Consistency'], ascending=[False, False])
    
    # 5. Save Markdown Report
    report_path = "feature_stability_report.md"
    with open(report_path, 'w') as f:
        f.write("# Brutal Feature Stability Analysis - Cross-Fold Intersection\n\n")
        f.write("> **Objective**: Identify the continuous planetary tensors that possess absolute, invariant predictive power across all 27 Walk-Forward rolling regimes (1993-2026).\n\n")
        
        f.write("## Invariant Alpha Tensors (Active in > 50% of regimes)\n\n")
        f.write("| Feature | Activation Frequency | Consistency | Mean Weight |\n")
        f.write("|---|---|---|---|\n")
        
        invariant = df_res[df_res['Activation_Freq'] >= 0.5]
        for _, row in invariant.iterrows():
            f.write(f"| {row['Feature']} | {row['Activation_Freq']*100:.1f}% ({row['Total_Activations']}/{n_folds}) | {row['Sign_Consistency']*100:.1f}% | {row['Mean_Active_Weight']:+.4f} |\n")
            
        f.write("\n## Transient / Regime-Dependent Tensors (Active in 20% - 50% of regimes)\n\n")
        f.write("| Feature | Activation Frequency | Consistency | Mean Weight |\n")
        f.write("|---|---|---|---|\n")
        
        transient = df_res[(df_res['Activation_Freq'] >= 0.2) & (df_res['Activation_Freq'] < 0.5)]
        for _, row in transient.iterrows():
            f.write(f"| {row['Feature']} | {row['Activation_Freq']*100:.1f}% ({row['Total_Activations']}/{n_folds}) | {row['Sign_Consistency']*100:.1f}% | {row['Mean_Active_Weight']:+.4f} |\n")

        f.write("\n## Extinguished Tensors (Active in < 20% of regimes)\n\n")
        f.write(f"*The L1 optimizer aggressively killed {len(df_res[df_res['Activation_Freq'] < 0.2])} features in over 80% of folds, proving they have no robust mathematical edge.*")

    print(f"[Analyzer] Markdown report written to {report_path}")

    # 6. Generate Heatmap
    # We will plot the fold_weights_matrix for the top 25 features to keep the plot readable
    top_features_idx = df_res.index[:25]
    top_features_names = df_res['Feature'].iloc[:25].tolist()
    
    top_matrix = fold_weights_matrix[:, top_features_idx].T # Shape (25, 27)
    
    plt.figure(figsize=(16, 10))
    sns.heatmap(top_matrix, 
                cmap="RdBu_r", 
                center=0.0, 
                yticklabels=top_features_names,
                xticklabels=[f"Fold {i+1}" for i in range(n_folds)],
                cbar_kws={'label': 'Tensor Weight (Directional Force)'})
                
    plt.title("Vedic Tensor Feature Stability Map (Top 25 Invariant Features Across 27 Market Regimes)")
    plt.xlabel("Walk-Forward OOS Fold (1993 -> 2026)")
    plt.ylabel("Continuous Planetary Tensor")
    plt.tight_layout()
    plt.savefig("feature_stability_heatmap.png", dpi=300)
    print("[Analyzer] Heatmap saved to feature_stability_heatmap.png")

if __name__ == "__main__":
    main()
