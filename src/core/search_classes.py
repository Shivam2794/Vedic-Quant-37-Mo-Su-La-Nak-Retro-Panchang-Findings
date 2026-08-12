import os, re
patterns = [r"class.*Alpha", r"class.*Math", r"class.*Ephemeris", r"Alpha.*Engine", r"Math.*Layer", r"Ephemeris.*Engine"]
for root, _, files in os.walk("."):
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f):
                        if any(re.search(p, line, re.IGNORECASE) for p in patterns):
                            print(f"{filepath}:{i+1}:{line.strip()}")
            except:
                pass
