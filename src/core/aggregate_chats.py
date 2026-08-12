import os
import datetime

# Target directories to search
DIRS = [
    r"C:\Users\Shivam Patel\Downloads",
    r"C:\Users\Shivam Patel\.gemini\antigravity\scratch",
    r"C:\Users\Shivam Patel\.gemini\antigravity\brain"
]

ALLOWED_EXTENSIONS = {'.md', '.txt', '.py', '.json'}
EXCLUDED_DIRS = {'.git', '__pycache__', 'node_modules', 'browser_recordings', 'logs', 'venv', '.venv'}
MAX_FILE_SIZE_MB = 2.0  # Skip files larger than 2MB

# 10 days ago
cutoff_date = datetime.datetime.now() - datetime.timedelta(days=10)
output_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\gcp_backup_vm1\home\patel\omni-v2\legacy_chats.txt"

count = 0
total_size = 0

with open(output_path, "w", encoding="utf-8") as outfile:
    for search_dir in DIRS:
        if not os.path.exists(search_dir):
            continue
            
        for root, dirs, files in os.walk(search_dir):
            # Exclude specified directories
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in ALLOWED_EXTENSIONS:
                    continue
                    
                filepath = os.path.join(root, file)
                
                try:
                    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
                    size_mb = os.path.getsize(filepath) / (1024 * 1024)
                    
                    if mtime >= cutoff_date and size_mb <= MAX_FILE_SIZE_MB:
                        # Skip writing the output file itself if we encounter it
                        if filepath == output_path:
                            continue
                            
                        outfile.write(f"\n\n{'='*80}\n")
                        outfile.write(f"FILE: {filepath}\n")
                        outfile.write(f"LAST MODIFIED: {mtime}\n")
                        outfile.write(f"{'='*80}\n\n")
                        
                        with open(filepath, "r", encoding="utf-8", errors="ignore") as infile:
                            content = infile.read()
                            # Optional: Truncate exceptionally long files just in case
                            if len(content) > 1000000:
                                content = content[:1000000] + "\n\n...[TRUNCATED]..."
                            outfile.write(content)
                        
                        count += 1
                        total_size += size_mb
                        print(f"Aggregated: {filepath} ({size_mb:.2f} MB)")
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")

print(f"\nSuccessfully aggregated {count} files.")
print(f"Total size: {total_size:.2f} MB")
print(f"Output saved to: {output_path}")
