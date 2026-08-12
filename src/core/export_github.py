import os
import shutil

def export_github_repo():
    src_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
    export_dir = os.path.join(src_dir, "EternalQuant_Github_Export")
    
    # Create structure
    dirs = [
        "docs/audits_and_inspections",
        "docs/equity_curves",
        "docs/historical_reports",
        "src/01_legacy_ideation_v1_v7",
        "src/02_machine_learning_v8_v11",
        "src/03_sensitivity_gauntlet_v12_v14",
        "src/04_hybrid_apex_v15_v16",
        "src/core",
        "data"
    ]
    
    for d in dirs:
        os.makedirs(os.path.join(export_dir, d), exist_ok=True)

    print("Copying files to export folder...")
    
    # Iterate through all files in scratch
    for f in os.listdir(src_dir):
        file_path = os.path.join(src_dir, f)
        
        # Skip directories and the export dir itself
        if not os.path.isfile(file_path):
            continue
            
        fname_lower = f.lower()
        dst_folder = None
        
        # Data
        if fname_lower.endswith(".parquet") or (fname_lower.endswith(".csv") and "matrix" in fname_lower):
            # Skip massive files > 50MB for github compatibility
            if os.path.getsize(file_path) < 50 * 1024 * 1024:
                dst_folder = "data"
        
        # Docs
        elif fname_lower.endswith(".png") and "curve" in fname_lower:
            dst_folder = "docs/equity_curves"
        elif fname_lower.endswith(".png") and ("opus" in fname_lower or "frame" in fname_lower):
            dst_folder = "docs/equity_curves"
        elif "audit" in fname_lower or "brutal_inspection" in fname_lower or "ledger" in fname_lower:
            if fname_lower.endswith(".md") or fname_lower.endswith(".json") or fname_lower.endswith(".txt"):
                dst_folder = "docs/audits_and_inspections"
        elif fname_lower.endswith(".md") and f not in ["README.md", "implementation_plan_scratch_github.md"]:
            dst_folder = "docs/historical_reports"
            
        # Core
        elif fname_lower.startswith("omni_") or fname_lower.startswith("patch") or fname_lower.startswith("extract"):
            if fname_lower.endswith(".py"):
                dst_folder = "src/core"
        elif f in ["brutal_inspection.py", "apply_fix.py", "test_swe.py", "data_io.py", "backtest_framework.py"]:
            dst_folder = "src/core"
            
        # Legacy V1-V7
        elif fname_lower.startswith("agentic_idea") or fname_lower.startswith("bot") or "v1" in fname_lower or "v2" in fname_lower or "v3" in fname_lower or "v4" in fname_lower or "v5" in fname_lower or "v6" in fname_lower or "v7" in fname_lower:
            if fname_lower.endswith(".py") and dst_folder is None:
                # Exclude if it actually has v10, v11, etc. inside the name 
                # (handled by checking strictly for v1-7 without adjacent numbers, but string matching is fuzzy)
                # Let's do a stricter check:
                if any(f"_v{i}" in fname_lower or f"v{i}_" in fname_lower for i in range(1,8)):
                    dst_folder = "src/01_legacy_ideation_v1_v7"
                elif "opus1" in fname_lower or "opus2" in fname_lower or "opus3" in fname_lower or "opus4" in fname_lower or "opus5" in fname_lower or "opus6" in fname_lower or "opus7" in fname_lower:
                    dst_folder = "src/01_legacy_ideation_v1_v7"
                
        # ML V8-V11
        elif "v8" in fname_lower or "v9" in fname_lower or "v10" in fname_lower or "v11" in fname_lower or "opus8" in fname_lower or "opus9" in fname_lower or "opus10" in fname_lower or "opus11" in fname_lower:
            if fname_lower.endswith(".py") and dst_folder is None:
                dst_folder = "src/02_machine_learning_v8_v11"
                
        # Sensitivity V12-V14
        elif "v12" in fname_lower or "v13" in fname_lower or "v14" in fname_lower or "opus12" in fname_lower or "opus13" in fname_lower or "opus14" in fname_lower:
            if fname_lower.endswith(".py") and dst_folder is None:
                dst_folder = "src/03_sensitivity_gauntlet_v12_v14"
                
        # Apex V15-V16
        elif "v15" in fname_lower or "v16" in fname_lower or "opus15" in fname_lower or "opus16" in fname_lower or "final_winning_strategy" in fname_lower:
            if fname_lower.endswith(".py") and dst_folder is None:
                dst_folder = "src/04_hybrid_apex_v15_v16"
        
        # If it's a py file but we haven't mapped it, put it in core just in case
        elif fname_lower.endswith(".py") and dst_folder is None:
            dst_folder = "src/core"
            
        if dst_folder:
            shutil.copy2(file_path, os.path.join(export_dir, dst_folder, f))
            
    print(f"Extraction and organization complete in {export_dir}")

if __name__ == "__main__":
    export_github_repo()
