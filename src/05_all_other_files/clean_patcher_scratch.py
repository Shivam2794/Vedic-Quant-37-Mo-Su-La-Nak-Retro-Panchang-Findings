import os
import re

def clean_patcher():
    root_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
    files_to_patch = []
    
    for root, dirs, files in os.walk(root_dir):
        if ".git" in root or "brain" in root or ".gemini" in root or "EternalQuant_Github_Export" in root or "Vedic-Quant-37" in root:
            continue
        for f in files:
            if f.endswith(".py"):
                files_to_patch.append(os.path.join(root, f))
                
    patched_count = 0
    
    for filepath in files_to_patch:
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                content = f.read()
            except Exception:
                continue
                
        original_content = content
        
        # 1. YFinance Dividend Leakage Patch
        def yf_replacer(match):
            m = match.group(0)
            if "auto_adjust=" in m:
                if "v13_engine_grid_search" in filepath or "validation_harness" in filepath:
                    return m.replace("auto_adjust=False", "auto_adjust=True")
                return m.replace("auto_adjust=True", "auto_adjust=False")
            else:
                if "v13_engine_grid_search" in filepath or "validation_harness" in filepath:
                    return m.replace("progress=False", "auto_adjust=True, progress=False")
                return m.replace("progress=False", "auto_adjust=False, progress=False")
                
        content = re.sub(r"yf\.download\([^)]*progress=False[^)]*\)", yf_replacer, content)
        
        # Eliminate duplicates
        content = re.sub(r"auto_adjust=False\s*,\s*auto_adjust=False", "auto_adjust=False", content)
        content = re.sub(r"auto_adjust=True\s*,\s*auto_adjust=False", "auto_adjust=True", content)
        
        # 2. Exposure Drift Patch
        content = content.replace(
            "prev_qqq_exp = qqq_exposure\n        prev_spy_exp = spy_exposure\n        prev_tlt_exp = tlt_exposure",
            "prev_qqq_exp = (qqq_exposure * (1.0 + r_qqq)) / (1.0 + net_ret)\n        prev_spy_exp = (spy_exposure * (1.0 + r_sp)) / (1.0 + net_ret)\n        prev_tlt_exp = (tlt_exposure * (1.0 + r_tlt)) / (1.0 + net_ret)"
        )
        content = re.sub(
            r"prev_qqq_exp = qqq_exposure\s+prev_spy_exp = spy_exposure\s+prev_tlt_exp = tlt_exposure",
            "prev_qqq_exp = (qqq_exposure * (1.0 + r_qqq)) / (1.0 + net_ret)\n        prev_spy_exp = (spy_exposure * (1.0 + r_sp)) / (1.0 + net_ret)\n        prev_tlt_exp = (tlt_exposure * (1.0 + r_tlt)) / (1.0 + net_ret)",
            content
        )
        
        content = content.replace(
            "equity *= (1.0 + port_ret - margin_drag - slippage_drag)",
            "net_ret = port_ret - margin_drag - slippage_drag\n        equity *= (1.0 + net_ret)"
        )
        
        # 3. CAGR Denominator Patch
        if "v9_ml_century_backtest_expanding" not in filepath and "v11_ml_century_backtest_expanding" not in filepath and "grid_search" not in filepath and "ml_parameter_optimizer" not in filepath and "brutal_ml_optimizer" not in filepath:
            def cagr_replacer(match):
                var_name = match.group(1)
                return f"(pd.to_datetime({var_name}.iloc[-1]) - pd.to_datetime({var_name}.iloc[0])).days / 365.25"
            content = re.sub(r"len\((.*?)\)\s*/\s*252(?:\.0)?", cagr_replacer, content)
            
        # 4. Workspace Isolation (quick_diagnostic_v6.py)
        if "quick_diagnostic_v6.py" in filepath:
            content = re.sub(r'PROJECT_ROOT = r"C:\\\\Users\\\\Shivam Patel\\\\\.gemini\\\\antigravity\\\\brain.*?"', 'PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))', content)
            
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            patched_count += 1
            print(f"Patched: {filepath}")
            
    print(f"CLEAN PATCHER COMPLETE: Successfully patched {patched_count} files in scratch dir.")

if __name__ == "__main__":
    clean_patcher()
