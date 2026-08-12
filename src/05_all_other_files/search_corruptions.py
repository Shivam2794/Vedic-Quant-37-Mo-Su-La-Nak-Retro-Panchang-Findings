import os
import re

def search_files():
    scratch_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
    
    print("--- Searching for Duplicate auto_adjust ---")
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
                            if line.count('auto_adjust') > 1:
                                print(f"SyntaxError (Duplicate auto_adjust) in {filepath}:{i+1}")
                                print(f"  {line.strip()}")
                except Exception:
                    pass
                    
    print("\n--- Searching for pd.to_datetime denominator corruptions ---")
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
                            if "pd.to_datetime" in line and ".days / 365.25" in line:
                                print(f"Possible Corruption in {filepath}:{i+1}")
                                print(f"  {line.strip()}")
                except Exception:
                    pass

    print("\n--- Searching for quick_diagnostic_v6.py ---")
    for root, _, files in os.walk(scratch_dir):
        if ".gemini" in root or "brain" in root or ".git" in root:
            continue
        for file in files:
            if file == "quick_diagnostic_v6.py":
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "brain" in content:
                            print(f"Found 'brain' in {filepath}")
                except Exception:
                    pass

if __name__ == "__main__":
    search_files()
