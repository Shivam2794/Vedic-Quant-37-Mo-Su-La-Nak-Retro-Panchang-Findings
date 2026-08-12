import os
import json
import re

out_file = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\ac09686f-b2e2-4349-aa40-8ff7fa4bba80\usa_vedic_master_transcript.md"

# Clear out previous runs
if os.path.exists(out_file):
    os.remove(out_file)

# words to reject
reject_words = [r'\bnifty\b', r'\bnse\b', r'\bbanknifty\b', r'\bzerodha\b']

# words to accept (USA Vedic Quant)
accept_words = [r'\bspy\b', r'\bqqq\b', r'\busa\b', r'\boptions\b', r'\bvedic\b', r'\bnadi\b', r'\bjamini\b', r'\bbhrigu\b', r'\bmachine learning\b', r'\b740\b']

def contains_reject(text):
    text_lower = text.lower()
    for w in reject_words:
        if re.search(w, text_lower):
            return True
    return False

def contains_accept(text):
    text_lower = text.lower()
    score = 0
    if re.search(r'\bspy\b', text_lower) or re.search(r'\bqqq\b', text_lower) or re.search(r'\busa\b', text_lower):
        score += 2
    if re.search(r'\bvedic\b', text_lower) or re.search(r'\bnadi\b', text_lower) or re.search(r'\bjamini\b', text_lower):
        score += 1
    if re.search(r'\b740\b', text_lower):
        score += 2
    if re.search(r'\bmachine learning\b', text_lower) or re.search(r'\bquant\b', text_lower):
        score += 1
    return score >= 3

def clean_text(text):
    # Remove system messages
    text = re.sub(r'<SYSTEM_MESSAGE>.*?</SYSTEM_MESSAGE>', '', text, flags=re.DOTALL)
    # Remove specific user warning text to avoid false positives
    text = re.sub(r'(?i)do not include anything related to nifty, nse, zerodha, or indian stock market configurations', '', text)
    text = re.sub(r'(?i)nifty, nse, banknifty, zerodha', '', text)
    return text

def process_text(text, filename):
    if 'f4be24c8-3dd5-4beb-8a7c-ca68b7586a0a' in filename or 'ac09686f-b2e2-4349-aa40-8ff7fa4bba80' in filename:
        print(f"Skipped {filename} (current or main agent chat).")
        return
        
    if not text.strip(): return
    
    cleaned_text = clean_text(text)
    
    if contains_reject(cleaned_text):
        print(f"Rejected {filename} due to Indian market concepts.")
        return
    if contains_accept(cleaned_text):
        print(f"Accepted {filename} for USA Vedic Quant.")
        with open(out_file, "a", encoding="utf-8") as f:
            f.write(f"\n\n# Source: {filename}\n\n")
            f.write(cleaned_text)
            f.write("\n\n---\n")
    else:
        print(f"Skipped {filename} (no strong match).")

# Process downloads MD files
with open(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\downloads_md.txt", "r", encoding="utf-16") as f:
    downloads = f.read().splitlines()

for d in downloads:
    if not d.strip(): continue
    try:
        with open(d, "r", encoding="utf-8") as df:
            content = df.read()
            process_text(content, d)
    except Exception as e:
        pass

# Process jsonl files in brain
import glob
jsonl_files = glob.glob(r"C:\Users\Shivam Patel\.gemini\antigravity\brain\*\.system_generated\logs\transcript.jsonl")

for jf in jsonl_files:
    try:
        with open(jf, "r", encoding="utf-8") as f:
            full_text = []
            for line in f:
                try:
                    data = json.loads(line)
                    if 'content' in data and data['content']:
                        full_text.append(data['content'])
                except:
                    pass
            content = "\n".join(full_text)
            process_text(content, jf)
    except Exception as e:
        pass

print("Done.")
