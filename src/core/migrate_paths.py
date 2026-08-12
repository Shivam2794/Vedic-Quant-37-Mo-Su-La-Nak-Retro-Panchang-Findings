import os
import sqlite3

OLD_USER = "patel"
NEW_USER = os.getlogin()

# Update these if you place the folders somewhere else on the new PC
BRAIN_DIR = fr"C:\Users\{NEW_USER}\.gemini\antigravity\brain"
FLEET_DIR = fr"C:\Users\{NEW_USER}\Desktop\Python\Learn\fleet"

print(f"Migration Tool: Updating paths from '{OLD_USER}' to '{NEW_USER}'...")

if OLD_USER == NEW_USER:
    print("Username hasn't changed. No path correction needed!")
    exit(0)

# 1. Update text/config files in fleet
def update_text_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        if OLD_USER in content:
            new_content = content.replace(f"Users\\{OLD_USER}", f"Users\\{NEW_USER}")
            new_content = new_content.replace(f"Users/{OLD_USER}", f"Users/{NEW_USER}")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated: {filepath}")
    except Exception as e:
        print(f"Skipped {filepath}: {e}")

for root, _, files in os.walk(FLEET_DIR):
    for file in files:
        if file.endswith(('.py', '.env', '.ps1', '.json', '.md', '.txt')):
            update_text_file(os.path.join(root, file))

print("\nPath correction complete! You can now start Antigravity and your fleet.")
