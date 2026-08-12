import os
import shutil

src = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
dst = r"F:\Fleet_Master_Archive\Bot_5_Advance_Auto_Research_Astro\code"

os.makedirs(dst, exist_ok=True)

count = 0
for root, dirs, files in os.walk(src):
    if ".venv" in root or "__pycache__" in root:
        continue
    for file in files:
        if file.endswith(".py"):
            try:
                shutil.copy2(os.path.join(root, file), os.path.join(dst, file))
                count += 1
            except:
                pass
print(f"Copied {count} files to {dst}")
