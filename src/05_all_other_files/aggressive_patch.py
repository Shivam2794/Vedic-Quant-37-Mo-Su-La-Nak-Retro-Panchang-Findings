import os
import re

def aggressive_patcher():
    scratch_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
    count = 0
    for root, _, files in os.walk(scratch_dir):
        if ".gemini" in root or "brain" in root or "EternalQuant" in root or ".git" in root or "venv" in root or "site-packages" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception:
                    continue
                
                orig_content = content
                
                # 1. YFinance Leakage Fix
                # Find yf.download(..., auto_adjust=False) and inject auto_adjust=False if neither True nor False is present
                def yf_replacer(m):
                    call = m.group(0)
                    if "auto_adjust=False" in call or "auto_adjust=True" in call:
                        return call
                    return call.replace("yf.download(", "yf.download(auto_adjust=False, ")
                
                content = re.sub(r"yf\.download\([^)]+\)", yf_replacer, content)
                
                # 2. MTM Exposure Drift
                content = content.replace(
                    "prev_qqq_exp = qqq_exposure\n        prev_spy_exp = spy_exposure\n        prev_tlt_exp = tlt_exposure",
                    "prev_qqq_exp = (qqq_exposure * (1.0 + r_qqq)) / (1.0 + net_ret)\n        prev_spy_exp = (spy_exposure * (1.0 + r_sp)) / (1.0 + net_ret)\n        prev_tlt_exp = (tlt_exposure * (1.0 + r_tlt)) / (1.0 + net_ret)"
                )
                content = content.replace(
                    "equity *= (1.0 + port_ret - margin_drag - slippage_drag)",
                    "net_ret = port_ret - margin_drag - slippage_drag\n        equity *= (1.0 + net_ret)"
                )
                
                if content != orig_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Patched: {filepath}")
                    count += 1

    print(f"Aggressive patch complete. {count} files patched.")

if __name__ == "__main__":
    aggressive_patcher()
