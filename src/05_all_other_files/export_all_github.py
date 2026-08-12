import os
import shutil

def export_everything():
    src_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
    repo_dir = os.path.join(src_dir, "Vedic-Quant-37-Mo-Su-La-Nak-Retro-Panchang-Findings")
    
    # Create a generic folder for all uncategorized files
    generic_folder = os.path.join(repo_dir, "src", "05_all_other_files")
    data_folder = os.path.join(repo_dir, "data")
    docs_folder = os.path.join(repo_dir, "docs", "all_other_docs")
    
    os.makedirs(generic_folder, exist_ok=True)
    os.makedirs(data_folder, exist_ok=True)
    os.makedirs(docs_folder, exist_ok=True)
    
    count = 0
    for file in os.listdir(src_dir):
        file_path = os.path.join(src_dir, file)
        
        # Skip directories
        if not os.path.isfile(file_path):
            continue
            
        # Check if already exists somewhere in repo
        found_in_repo = False
        for root, _, files in os.walk(repo_dir):
            if file in files:
                found_in_repo = True
                break
                
        if found_in_repo:
            continue
            
        # Large file protection for github (100MB limit, keep it to 50MB to be safe)
        if os.path.getsize(file_path) > 50 * 1024 * 1024:
            print(f"Skipping large file: {file}")
            continue
            
        # Categorize
        ext = file.lower().split('.')[-1]
        
        if ext in ['csv', 'parquet', 'db', 'sqlite', 'json']:
            dst = os.path.join(data_folder, file)
        elif ext in ['txt', 'md', 'png', 'mp4', 'html', 'pdf']:
            dst = os.path.join(docs_folder, file)
        else:
            dst = os.path.join(generic_folder, file)
            
        shutil.copy2(file_path, dst)
        count += 1
        
    print(f"Exported {count} additional files to the repo.")

if __name__ == "__main__":
    export_everything()
