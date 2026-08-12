import os

search_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
target = "CausalPreFilter"

for root, dirs, files in os.walk(search_dir):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            try:
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read()
                    if target in content:
                        print(f"Found {target} in {path}")
            except Exception as e:
                pass
