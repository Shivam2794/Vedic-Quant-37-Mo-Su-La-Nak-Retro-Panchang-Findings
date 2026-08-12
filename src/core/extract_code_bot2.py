import os
import shutil

search_terms = ["advanced momentum", "bot 2", "bot_2", "advanced_momentum"]
source_dirs = [
    r"C:\Users\Shivam Patel\.gemini\antigravity\scratch",
    r"C:\Users\Shivam Patel\.gemini\antigravity\mcp"
]
dest_dir = r"F:\Fleet_Master_Archive\Bot_2_Advanced_Momentum\code"

found_files = set()

for d in source_dirs:
    for root, dirs, files in os.walk(d):
        for file in files:
            if not file.endswith('.py') and not file.endswith('.pine') and not file.endswith('.json'): continue
            if "brain" in root or ".gemini" in root.replace("C:\\Users\\Shivam Patel\\.gemini\\antigravity", ""):
                # skip system generated or other stuff maybe?
                pass
            file_path = os.path.join(root, file)
            # check name
            if any(term in file.lower() for term in search_terms):
                found_files.add(file_path)
                continue
            
            # check content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if any(term in content for term in search_terms):
                        found_files.add(file_path)
            except:
                pass

for f in found_files:
    try:
        shutil.copy2(f, dest_dir)
        print(f"Copied {f}")
    except Exception as e:
        print(f"Failed to copy {f}: {e}")

print(f"Copied {len(found_files)} files to {dest_dir}")
