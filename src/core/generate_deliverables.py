import json
import os
import re

def run():
    with open('audit_summary.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    physical_files = data.get("physical_files_found", [])
    
    # Generate the categorization matrix
    matrix_path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\a252d513-5132-4d80-a20e-e71d4a2ea238\completed_asset_categorization_matrix.md"
    
    with open(matrix_path, 'w', encoding='utf-8') as f:
        f.write("# COMPLETED ASSET CATEGORIZATION MATRIX\n\n")
        f.write("| Asset / File Path | Origin (Chat ID) | Destination Loop | Telemetry / Tracking Hook |\n")
        f.write("|---|---|---|---|\n")
        
        # Write touched files
        for path in physical_files:
            # We don't have exact CID for physical files in scratch, so we list "Legacy Repository" unless it's in a brain folder
            cid = "Legacy Repository"
            if "\\brain\\" in path:
                try:
                    cid = path.split("\\brain\\")[1].split("\\")[0]
                except:
                    pass
                    
            name = os.path.basename(path).lower()
            if 'plan' in name or 'report' in name or 'walkthrough' in name or name.endswith('.md') or name.endswith('.txt') or name.endswith('.json') or name.endswith('.db'):
                loop = "Outer Loop (Knowledge Base)"
                hook = "Context Integrity Hash (SHA-256)"
            else:
                loop = "Inner Loop (Execution Core)"
                hook = "Execution State Telemetry / Latency Monitor"
                
            f.write(f"| `{path}` | `{cid}` | {loop} | {hook} |\n")
            
        # Add historical context items
        f.write(f"| `Historical Context - Root Transcripts` | `7b03663a-d01b-4302-8959-0a511c484299` | Outer Loop | RAG Index / Vector Hook |\n")
        f.write(f"| `Historical Context - Subagent 1 Transcripts` | `083b0f8a-28ff-4962-bf24-e3339c053c6a` | Outer Loop | RAG Index / Vector Hook |\n")
        f.write(f"| `Historical Context - Subagent 2 Transcripts` | `0408ba04-b110-46c2-8c78-843f3a46a017` | Outer Loop | RAG Index / Vector Hook |\n")
        f.write(f"| `Historical Context - Main Session Transcripts` | `a252d513-5132-4d80-a20e-e71d4a2ea238` | Outer Loop | RAG Index / Vector Hook |\n")
        
    print(f"Generated deliverables with {len(physical_files)} physical files itemized without truncation.")

if __name__ == '__main__':
    run()
