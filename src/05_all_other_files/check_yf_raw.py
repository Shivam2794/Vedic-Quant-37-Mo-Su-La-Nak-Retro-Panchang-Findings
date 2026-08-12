import os
import re

count = 0
for root, dirs, files in os.walk(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"):
    if ".gemini" in root or "brain" in root or "EternalQuant" in root or "Vedic-Quant" in root:
        continue
    for f in files:
        if f.endswith(".py"):
            with open(os.path.join(root, f), 'r', encoding='utf-8') as file:
                try:
                    content = file.read()
                    if "yf.download" in content:
                        print(f"Found in {f}")
                        count += 1
                        if count > 5:
                            exit()
                except Exception:
                    pass
