import json
import os
import ast

def get_ast_hooks(file_path):
    if not file_path.endswith('.py'):
        return "N/A"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content)
        hooks = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                hooks.append(f"def {node.name}()")
            elif isinstance(node, ast.ClassDef):
                hooks.append(f"class {node.name}")
        
        if not hooks:
            return "Module Level Execution (requires main() wrapper)"
            
        # Truncate to top 3 hooks to avoid blowing up table width
        if len(hooks) > 3:
            return ", ".join(hooks[:3]) + f" (+{len(hooks)-3} more)"
        return ", ".join(hooks)
    except Exception:
        return "Parse Error / Unstructured Script"

def run():
    with open('audit_summary.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    physical_files = data.get("physical_files_found", [])
    
    matrix_path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\a252d513-5132-4d80-a20e-e71d4a2ea238\completed_asset_categorization_matrix.md"
    
    # We will buffer writes
    with open(matrix_path, 'w', encoding='utf-8') as f:
        f.write("# COMPLETED ASSET CATEGORIZATION MATRIX (AST Remediated)\n\n")
        f.write("| Asset / File Path | Origin (Chat ID) | Destination Loop | Telemetry / Tracking Hook Target |\n")
        f.write("|---|---|---|---|\n")
        
        count = 0
        for path in physical_files:
            cid = "Legacy Repository"
            if "\\brain\\" in path:
                try:
                    cid = path.split("\\brain\\")[1].split("\\")[0]
                except:
                    pass
                    
            name = os.path.basename(path).lower()
            if 'plan' in name or 'report' in name or 'walkthrough' in name or name.endswith(('.md', '.txt', '.json', '.db', '.png', '.log', '.csv', '.parquet')):
                loop = "Outer Loop (Knowledge Base)"
                hook = "Context Integrity Hash (SHA-256)"
            elif name.endswith('.py'):
                loop = "Inner Loop (Execution Core)"
                ast_targets = get_ast_hooks(path)
                hook = f"AST Injection Points: {ast_targets}"
            else:
                loop = "Inner Loop (Execution Core)"
                hook = "Generic Monitor"
                
            f.write(f"| `{path}` | `{cid}` | {loop} | {hook} |\n")
            count += 1
            if count % 10000 == 0:
                print(f"Processed {count} files...")
                
        # Add historical context items
        f.write(f"| `Historical Context - Root Transcripts` | `7b03663a-d01b-4302-8959-0a511c484299` | Outer Loop | RAG Index / Vector Hook |\n")
        f.write(f"| `Historical Context - Subagent 1 Transcripts` | `083b0f8a-28ff-4962-bf24-e3339c053c6a` | Outer Loop | RAG Index / Vector Hook |\n")
        f.write(f"| `Historical Context - Subagent 2 Transcripts` | `0408ba04-b110-46c2-8c78-843f3a46a017` | Outer Loop | RAG Index / Vector Hook |\n")
        f.write(f"| `Historical Context - Main Session Transcripts` | `a252d513-5132-4d80-a20e-e71d4a2ea238` | Outer Loop | RAG Index / Vector Hook |\n")
        
    print(f"Remediated matrix generated with precise AST telemetry targets for {count} files.")

if __name__ == '__main__':
    run()
