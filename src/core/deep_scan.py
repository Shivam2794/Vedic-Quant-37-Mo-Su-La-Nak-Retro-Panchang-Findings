import os
import json
import time

TARGET_DIRS = [
    r'C:\Users\Shivam Patel\Desktop',
    r'C:\Users\Shivam Patel\Documents',
    r'C:\Users\Shivam Patel\Downloads',
    r'C:\Users\Shivam Patel\.gemini',
    r'D:\\',
    r'E:\\'
]

# We want files that have 'vedic' AND 'quant' AND 'usa'
REQUIRED_TERMS = ['vedic', 'quant', 'usa']
# We must EXCLUDE files with 'india' or 'indiac'
EXCLUDE_TERMS = ['india']

SUPPORTED_EXTS = {'.py', '.md', '.txt', '.json', '.jsonl', '.csv', '.yaml', '.yml'}

accepted_files = []
rejected_files = [] # Track rejected for audit
chats_found = []

start_time = time.time()
scanned_count = 0

def check_content(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            
            # Rule 1: Exclusion
            for ex in EXCLUDE_TERMS:
                if ex in content:
                    return False, f"Contained excluded term: {ex}"
            
            # Rule 2: Inclusion
            # It must have all required terms
            if all(req in content for req in REQUIRED_TERMS):
                return True, "Matches all USA Vedic Quant criteria"
                
            return False, "Missing required USA/Vedic/Quant keywords"
    except UnicodeDecodeError:
        # Try latin-1 if utf-8 fails
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                content = f.read().lower()
                for ex in EXCLUDE_TERMS:
                    if ex in content:
                        return False, f"Contained excluded term: {ex}"
                if all(req in content for req in REQUIRED_TERMS):
                    return True, "Matches all USA Vedic Quant criteria"
                return False, "Missing keywords"
        except Exception as e:
            return False, f"Read error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def process_chat_log(filepath):
    # Chat logs are in .system_generated/logs/transcript.jsonl
    # Instead of reading the whole file as a block, we check the text.
    # If it contains USA and Vedic, we keep it. If it contains India, we drop it.
    is_valid, reason = check_content(filepath)
    if is_valid:
        chats_found.append(filepath)
    else:
        if "excluded term" in reason:
            rejected_files.append((filepath, reason))

for d in TARGET_DIRS:
    if not os.path.exists(d): continue
    for root, dirs, files in os.walk(d):
        # Prune heavy dirs
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '.venv', 'venv', '__pycache__']]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            filepath = os.path.join(root, file)
            
            # Check Gemini Chat Logs explicitly
            if '.system_generated' in root and file == 'transcript.jsonl':
                process_chat_log(filepath)
                scanned_count += 1
                continue
                
            if ext in SUPPORTED_EXTS:
                scanned_count += 1
                is_valid, reason = check_content(filepath)
                if is_valid:
                    accepted_files.append(filepath)
                elif "excluded term" in reason:
                    rejected_files.append((filepath, reason))
                    
        # Timeout to prevent hanging infinitely in massive drives
        if time.time() - start_time > 300: # 5 mins max
            break
    if time.time() - start_time > 300:
        break

print(f"Deep Scan Complete in {time.time() - start_time:.2f} seconds.")
print(f"Total files scanned: {scanned_count}")
print(f"Total USA Vedic Quant Files Found: {len(accepted_files)}")
print(f"Total USA Vedic Quant Chats Found: {len(chats_found)}")
print(f"Total Quarantined (India/Excluded): {len(rejected_files)}")

# Save Results
out_dir = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\usa_vedic_scan'
os.makedirs(out_dir, exist_ok=True)

with open(os.path.join(out_dir, 'accepted_files.txt'), 'w', encoding='utf-8') as f:
    for p in accepted_files: f.write(p + '\n')
    
with open(os.path.join(out_dir, 'accepted_chats.txt'), 'w', encoding='utf-8') as f:
    for p in chats_found: f.write(p + '\n')

with open(os.path.join(out_dir, 'rejected_quarantine.txt'), 'w', encoding='utf-8') as f:
    for p, r in rejected_files: f.write(f"{p} | {r}\n")
