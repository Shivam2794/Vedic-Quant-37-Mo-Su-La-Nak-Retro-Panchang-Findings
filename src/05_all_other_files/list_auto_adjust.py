import os

def list_auto_adjust():
    scratch_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
    for root, _, files in os.walk(scratch_dir):
        if ".gemini" in root or "brain" in root or ".git" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        if "auto_adjust=False" in f.read():
                            print(filepath)
                except Exception:
                    pass

if __name__ == "__main__":
    list_auto_adjust()
