import os
from pathlib import Path

scratch_dir = Path(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch")

print("Scanning for path replacements...")
count_files = 0
count_replaces = 0

for f in scratch_dir.iterdir():
    if f.is_file() and f.suffix == ".py" and f.name != "path_fixer.py":
        try:
            with open(f, "r", encoding="utf-8") as file:
                content = file.read()
                
            # Replace target path patterns
            # Handle both forward slash and backslash, and double backslashes
            new_content = content
            
            # Let's do direct string replacements
            targets = [
                (r"C:\Users\patel\.gemini", r"C:\Users\Shivam Patel\.gemini"),
                (r"C:\\Users\\patel\\.gemini", r"C:\\Users\\Shivam Patel\\.gemini"),
                (r"C:/Users/patel/.gemini", r"C:/Users/Shivam Patel/.gemini"),
                
                (r"C:\Users\patel\Desktop", r"C:\Users\Shivam Patel\Desktop"),
                (r"C:\\Users\\patel\\Desktop", r"C:\\Users\\Shivam Patel\\Desktop"),
                (r"C:/Users/patel/Desktop", r"C:/Users/Shivam Patel/Desktop"),
                
                (r"C:\Users\patel", r"C:\Users\Shivam Patel"),
                (r"C:\\Users\\patel", r"C:\\Users\\Shivam Patel"),
                (r"C:/Users/patel", r"C:/Users/Shivam Patel"),
            ]
            
            replaced = False
            for old, new in targets:
                if old in new_content:
                    new_content = new_content.replace(old, new)
                    replaced = True
            
            if replaced:
                with open(f, "w", encoding="utf-8") as file:
                    file.write(new_content)
                print(f"  [FIXED] {f.name}")
                count_files += 1
                
        except Exception as e:
            print(f"  [ERROR] {f.name}: {e}")

print(f"\nCompleted path corrections in {count_files} files.")
