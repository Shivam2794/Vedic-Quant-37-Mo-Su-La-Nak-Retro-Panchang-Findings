import os
import re

chunks_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\encyclopedia_chunks"
output_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\encyclopedia_raw_notes"
os.makedirs(output_dir, exist_ok=True)

patterns = {
    'failures': re.compile(r'(error|traceback|failed|exception|bug|issue|crash|cannot import name|keyerror|valueerror|syntaxerror|typeerror)', re.IGNORECASE),
    'datasets': re.compile(r'(dataset|csv|column|feature|df\[|vix|qqq|spy|tlt|gld|sh|\^vix9d|vix_term_struct|\^vvix|\^skew|dataframe)', re.IGNORECASE),
    'plans': re.compile(r'(architecture|phase|step|iteration|plan|blueprint|roadmap|iteration)', re.IGNORECASE),
    'results': re.compile(r'(cagr|max dd|sharpe|score=|results|champion|performance|pnl|\.py|\.md|\.json|csv)', re.IGNORECASE),
    'origins': re.compile(r'(goal|objective|origin|we are building|welcome to|foundational)', re.IGNORECASE)
}

# Clean previous vol1
for f in os.listdir(output_dir):
    if f.startswith('vol1_'):
        os.remove(os.path.join(output_dir, f))

for i in range(14, 21):
    chunk_name = f"chunk_{i:02d}.md"
    chunk_path = os.path.join(chunks_dir, chunk_name)
    if not os.path.exists(chunk_path):
        continue
        
    with open(chunk_path, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = re.split(r'\n\s*\n', content)
    
    categories = {k: [] for k in patterns.keys()}
    
    for block in blocks:
        block_lower = block.lower()
        matched = []
        for cat, pat in patterns.items():
            if pat.search(block_lower):
                matched.append(cat)
        
        for cat in matched:
            categories[cat].append(block.strip())

    vol = "vol2"
    for cat, matched_blocks in categories.items():
        if not matched_blocks: continue
        out_name = f"{vol}_{cat}_{chunk_name}"
        out_path = os.path.join(output_dir, out_name)
        
        with open(out_path, 'w', encoding='utf-8') as f:
            for b in matched_blocks:
                f.write(b + "\n\n---\n\n")

print("Improved extraction complete.")
