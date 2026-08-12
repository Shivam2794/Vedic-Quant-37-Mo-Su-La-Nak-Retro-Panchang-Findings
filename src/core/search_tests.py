import os

for root, dirs, files in os.walk("tests"):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                if "evaluation_report.json" in content:
                    print(f"Found in {path}")
