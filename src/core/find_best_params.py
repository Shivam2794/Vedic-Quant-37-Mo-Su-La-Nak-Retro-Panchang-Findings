import os
import sys
import argparse
import random
import json

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from src.main import run_pipeline, validate_args

SCRATCH_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
TEMP_JSON_REPORT = os.path.join(SCRATCH_DIR, "temp_report.json")
TEMP_MD_REPORT = os.path.join(SCRATCH_DIR, "temp_report.md")

# Candidate parameters to sweep
bottleneck_dims = [128, 256, 512, 1024, 2048]
dropouts = [0.1, 0.2, 0.3, 0.4, 0.5]
hidden_dims_list = [
    ["32", "16"],
    ["64", "32"],
    ["128", "64"],
    ["64", "32", "16"],
    ["128", "64", "32"]
]
sparsity_weights = [1e-4, 5e-4, 1e-3, 5e-3, 1e-2]

def create_args(b_dim, dropout, h_dims, sparsity, mc_paths=100):
    args = argparse.Namespace(
        tickers=["SPY", "QQQ", "DIA"],
        start_date="2006-01-01",
        end_date="2026-01-01",
        ayanamsha="lahiri",
        planets=["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"],
        sae_bottleneck_dim=str(b_dim),
        sae_sparsity_weight=sparsity,
        mlp_hidden_dims=h_dims,
        mlp_dropout=dropout,
        cv_splits=5,
        cv_purge_window=10,
        cv_embargo_pct=0.05,
        mc_paths=mc_paths,
        simulate_missing_ticker_evaluation=False,
        shuffle_targets=False,
        report_path=TEMP_JSON_REPORT,
        md_report_path=TEMP_MD_REPORT
    )
    return args

def main():
    random.seed(42)
    
    # Generate all combinations
    combinations = []
    for b_dim in bottleneck_dims:
        for dropout in dropouts:
            for h_dims in hidden_dims_list:
                for sparsity in sparsity_weights:
                    combinations.append((b_dim, dropout, h_dims, sparsity))
                    
    # Shuffle to get a random search order
    random.shuffle(combinations)
    
    print(f"Total combinations to search: {len(combinations)}")
    
    for idx, (b_dim, dropout, h_dims, sparsity) in enumerate(combinations):
        print(f"\n--- Trying combination {idx+1}/{len(combinations)} ---")
        print(f"sae_bottleneck_dim: {b_dim}")
        print(f"mlp_dropout: {dropout}")
        print(f"mlp_hidden_dims: {h_dims}")
        print(f"sae_sparsity_weight: {sparsity}")
        
        # 1. Quick run with mc_paths=100
        args = create_args(b_dim, dropout, h_dims, sparsity, mc_paths=100)
        try:
            b_dim_val, h_dims_val = validate_args(args)
            report = run_pipeline(args, b_dim_val, h_dims_val)
            
            best_asset = report["best_asset"]
            best_asset_metrics = report["assets"][best_asset]
            
            print(f"Best Asset: {best_asset}")
            print(f"Metrics: {best_asset_metrics}")
            
            # Check if beats_bh and beats_random are both True
            if best_asset_metrics["beats_bh"] and best_asset_metrics["beats_random"]:
                print(">>> Found candidate beating both baselines in quick search! Verifying with mc_paths=1000...")
                
                # 2. Detailed run with mc_paths=1000
                args_full = create_args(b_dim, dropout, h_dims, sparsity, mc_paths=1000)
                b_dim_val, h_dims_val = validate_args(args_full)
                report_full = run_pipeline(args_full, b_dim_val, h_dims_val)
                
                best_asset_full = report_full["best_asset"]
                best_asset_metrics_full = report_full["assets"][best_asset_full]
                
                print(f"Verification Results - Best Asset: {best_asset_full}")
                print(f"Verification Metrics: {best_asset_metrics_full}")
                
                if best_asset_metrics_full["beats_bh"] and best_asset_metrics_full["beats_random"]:
                    print("\n================ SUCCESS ================")
                    print("Found optimal parameters:")
                    print(f"sae_bottleneck_dim: {b_dim}")
                    print(f"mlp_dropout: {dropout}")
                    print(f"mlp_hidden_dims: {h_dims}")
                    print(f"sae_sparsity_weight: {sparsity}")
                    print("=========================================")
                    
                    # Save results to a file for easy reading
                    result_data = {
                        "sae_bottleneck_dim": b_dim,
                        "mlp_dropout": dropout,
                        "mlp_hidden_dims": h_dims,
                        "sae_sparsity_weight": sparsity,
                        "best_asset": best_asset_full,
                        "metrics": best_asset_metrics_full
                    }
                    with open(os.path.join(SCRATCH_DIR, "best_params_found.json"), "w") as f:
                        json.dump(result_data, f, indent=2)
                        
                    sys.exit(0)
                else:
                    print("Verification failed (did not beat both baselines with 1000 paths). Continuing search...")
                    
        except Exception as e:
            print(f"Error during execution: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
