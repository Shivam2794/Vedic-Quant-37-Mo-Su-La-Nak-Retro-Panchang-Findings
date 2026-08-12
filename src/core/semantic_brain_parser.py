import os
import json
import time
import re

TARGET_DIRS = [
    r'C:\Users\Shivam Patel\Desktop',
    r'C:\Users\Shivam Patel\Documents',
    r'C:\Users\Shivam Patel\.gemini'
]

SUPPORTED_EXTS = {'.py', '.md', '.txt', '.json', '.jsonl', '.csv'}

USA_TERMS = {'usa', 'nyse', 'spy', 'aapl', 'us/eastern', 'wall street', 'nasdaq'}
INDIA_TERMS = {'india', 'nifty', 'nse', 'bse', 'ist', 'asia/kolkata'}
VEDIC_TERMS = {'vedic', 'quant', 'jyotish', 'astrology', 'dasha'}

def semantic_brain_analyze(text):
    text_lower = text.lower()
    
    if 'vedic' not in text_lower and 'quant' not in text_lower:
        return 'ignore', ''
        
    usa_score = sum(text_lower.count(t) for t in USA_TERMS)
    india_score = sum(text_lower.count(t) for t in INDIA_TERMS)
    vedic_score = sum(text_lower.count(t) for t in VEDIC_TERMS)
    
    if vedic_score == 0:
        return 'ignore', ''
        
    if india_score > 0:
        sentences = re.split(r'[.!?\n]', text_lower)
        india_sentences = [s for s in sentences if any(i in s for i in INDIA_TERMS)]
        safe_india_mentions = 0
        for s in india_sentences:
            if 'not' in s or 'exclude' in s or 'unlike' in s or 'usa' in s:
                safe_india_mentions += 1
        if safe_india_mentions < len(india_sentences):
            return 'reject', f'India Context Score {india_score}'
            
    if usa_score > 0:
        return 'accept', f'USA Context Score {usa_score}'
        
    return 'ignore', ''

start_time = time.time()
scanned = 0

out_dir = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\usa_vedic_scan'
os.makedirs(out_dir, exist_ok=True)

f_accepted = open(os.path.join(out_dir, 'accepted_files.txt'), 'w', encoding='utf-8')
f_chats = open(os.path.join(out_dir, 'accepted_chats.txt'), 'w', encoding='utf-8')
f_quarantine = open(os.path.join(out_dir, 'rejected_quarantine.txt'), 'w', encoding='utf-8')

timeout = False

for d in TARGET_DIRS:
    if not os.path.exists(d): continue
    for root, dirs, files in os.walk(d):
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'venv', '__pycache__']]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in SUPPORTED_EXTS: continue
            
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    scanned += 1
                    decision, reason = semantic_brain_analyze(content)
                    
                    if decision == 'accept':
                        if '.gemini' in filepath and 'transcript' in file:
                            f_chats.write(filepath + '\n')
                            print(f"[CHAT ACCEPT] {filepath}")
                        else:
                            f_accepted.write(filepath + '\n')
                            print(f"[FILE ACCEPT] {filepath}")
                    elif decision == 'reject':
                        f_quarantine.write(f'{filepath} | {reason}\n')
                        print(f"[QUARANTINE] {filepath} -> {reason}")
            except Exception:
                pass
                
            if time.time() - start_time > 60:
                timeout = True
                break
        if timeout: break
    if timeout: break

f_accepted.close()
f_chats.close()
f_quarantine.close()

print(f'\n--- DONE ---')
print(f'Scanned {scanned} files before timeout/completion.')
