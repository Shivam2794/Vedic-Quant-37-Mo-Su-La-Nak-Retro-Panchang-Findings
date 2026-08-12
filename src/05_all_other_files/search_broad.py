import os
import re

def search_files():
    scratch_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
    
    print("--- Searching for auto_adjust ---")
    for root, _, files in os.walk(scratch_dir):
        if ".gemini" in root or "brain" in root or ".git" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "auto_adjust" in content:
                            print(f"Found auto_adjust in {filepath}")
                except Exception:
                    pass
                    
    print("\n--- Searching for pd.to_datetime ---")
    for root, _, files in os.walk(scratch_dir):
        if ".gemini" in root or "brain" in root or ".git" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "pd.to_datetime" in content:
                            print(f"Found pd.to_datetime in {filepath}")
                except Exception:
                    pass

if __name__ == "__main__":
    search_files()
