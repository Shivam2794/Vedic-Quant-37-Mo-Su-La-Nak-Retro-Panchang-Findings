import os
import re

chunks_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\encyclopedia_chunks"
out_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\encyclopedia_raw_notes"
os.makedirs(out_dir, exist_ok=True)

def extract_from_chunk(chunk_id):
    chunk_path = os.path.join(chunks_dir, f"chunk_{chunk_id}.md")
    if not os.path.exists(chunk_path):
        print(f"Skipping {chunk_id}, file not found")
        return
    
    with open(chunk_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        
    origins = []
    datasets_cols = []
    plans = []
    results = []
    failures = []
    
    for line in lines:
        l = line.strip()
        if not l:
            continue
            
        # VERY basic heuristics to capture these things:
        lower_l = l.lower()
        
        # Datasets & Columns (mentions of .csv, .json, .parquet, features)
        if re.search(r'\b\w+\.(csv|json|parquet|zip|db)\b', lower_l) or re.search(r'\b(column|feature|dataset)\b', lower_l):
            datasets_cols.append(l)
            
        # Failures & Errors
        if re.search(r'\b(error|fail|failed|failure|crash|exception|traceback|syntaxerror|typeerror|valueerror|unicode)\b', lower_l):
            failures.append(l)
            
        # Plans & Iterations
        if re.search(r'\b(plan|phase|epoch|step|iteration|next|todo)\b', lower_l):
            plans.append(l)
            
        # Results
        if re.search(r'\b(result|output|achieved|cagr|sharpe|drawdown|dd|beat|success)\b', lower_l):
            results.append(l)
            
        # Origins & Objectives
        if re.search(r'\b(goal|objective|aim|target|purpose|thesis)\b', lower_l):
            origins.append(l)

    # Let's write them out into separate files per category for the chunk, just like 14-20
    def write_cat(cat_name, content_list):
        filename = f"vol3_{cat_name}_chunk_{chunk_id}.md"
        with open(os.path.join(out_dir, filename), "w", encoding="utf-8") as f:
            f.write(f"# Chunk {chunk_id} - {cat_name.upper()}\n\n")
            # De-duplicate while preserving order
            seen = set()
            for item in content_list:
                if item not in seen:
                    f.write(f"- {item}\n")
                    seen.add(item)
                    
    write_cat("origins", origins)
    write_cat("datasets", datasets_cols)
    write_cat("plans", plans)
    write_cat("results", results)
    write_cat("failures", failures)
    print(f"Processed chunk {chunk_id}")

for i in range(10, 14):
    extract_from_chunk(str(i).zfill(2))
