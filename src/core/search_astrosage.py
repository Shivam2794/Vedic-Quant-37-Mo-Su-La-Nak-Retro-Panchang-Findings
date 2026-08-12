import os
search_text = "AstroSage"
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".txt") or file.endswith(".py") or file.endswith(".json") or file.endswith(".md"):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f):
                        if search_text.lower() in line.lower():
                            print(f"{filepath}:{i+1}: {line.strip()}")
            except Exception:
                pass
