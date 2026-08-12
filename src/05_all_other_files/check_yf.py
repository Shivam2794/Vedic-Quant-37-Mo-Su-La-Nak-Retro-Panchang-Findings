import os
import re

def search_files():
    scratch_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\Vedic-Quant-37-Mo-Su-La-Nak-Retro-Panchang-Findings"
    
    print("--- Searching for yf.download ---")
    count = 0
    for root, _, files in os.walk(scratch_dir):
        if ".gemini" in root or "brain" in root or ".git" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            if "yf.download" in line:
                                print(f"{filepath}:{i+1}")
                                print(f"  {line.strip()}")
                                count += 1
                                if count > 10:
                                    return
                except Exception:
                    pass

if __name__ == "__main__":
    search_files()
