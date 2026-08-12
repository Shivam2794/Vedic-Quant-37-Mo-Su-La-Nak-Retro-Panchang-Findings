import os
import re

chunks_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\encyclopedia_chunks"
out_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\encyclopedia_raw_notes"
os.makedirs(out_dir, exist_ok=True)

def extract_from_chunk_paragraphs(chunk_id):
    chunk_path = os.path.join(chunks_dir, f"chunk_{chunk_id}.md")
    if not os.path.exists(chunk_path):
        print(f"Skipping {chunk_id}, file not found")
        return
    
    with open(chunk_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    paragraphs = content.split('\n\n')
        
    origins = []
    datasets_cols = []
    plans = []
    results = []
    failures = []
    
    for p in paragraphs:
        l = p.strip()
        if not l:
            continue
            
        lower_l = l.lower()
        
        assigned = False
        # Datasets & Columns
        if re.search(r'\b\w+\.(csv|json|parquet|zip|db)\b', lower_l) or re.search(r'\b(column|feature|dataset)\b', lower_l):
            datasets_cols.append(l)
            assigned = True
            
        # Failures & Errors
        if re.search(r'\b(error|fail|failed|failure|crash|exception|traceback|syntaxerror|typeerror|valueerror|unicode)\b', lower_l):
            failures.append(l)
            assigned = True
            
        # Plans & Iterations
        if re.search(r'\b(plan|phase|epoch|step|iteration|next|todo)\b', lower_l):
            plans.append(l)
            assigned = True
            
        # Results
        if re.search(r'\b(result|output|achieved|cagr|sharpe|drawdown|dd|beat|success)\b', lower_l):
            results.append(l)
            assigned = True
            
        # Origins & Objectives
        if re.search(r'\b(goal|objective|aim|target|purpose|thesis)\b', lower_l):
            origins.append(l)
            assigned = True

    def write_cat(cat_name, content_list):
        filename = f"vol3_{cat_name}_chunk_{chunk_id}.md"
        with open(os.path.join(out_dir, filename), "w", encoding="utf-8") as f:
            f.write(f"# Chunk {chunk_id} - {cat_name.upper()}\n\n")
            seen = set()
            for item in content_list:
                if item not in seen:
                    f.write(f"{item}\n\n---\n\n")
                    seen.add(item)
                    
    write_cat("origins", origins)
    write_cat("datasets", datasets_cols)
    write_cat("plans", plans)
    write_cat("results", results)
    write_cat("failures", failures)
    print(f"Processed chunk {chunk_id}")

for i in range(7, 14):
    extract_from_chunk_paragraphs(str(i).zfill(2))
