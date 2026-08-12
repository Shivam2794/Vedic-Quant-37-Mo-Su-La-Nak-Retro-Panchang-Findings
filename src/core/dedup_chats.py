import os
import re

files = [
    r'C:\Users\Shivam Patel\Downloads\Automating Nadi Knowledge Graph.md',
    r'C:\Users\Shivam Patel\Downloads\Scaling Vedic Knowledge Extraction Pipeline.md',
    r'C:\Users\Shivam Patel\Downloads\Institutional Vedic Quant Architecture.md',
    r'C:\Users\Shivam Patel\Downloads\Institutional Vedic Quant Compiler.md',
    r'C:\Users\Shivam Patel\Downloads\Building Vedic Causal Quant Engine.md',
    r'C:\Users\Shivam Patel\Downloads\Scaling Vedic Quant Engine.md',
    r'C:\Users\Shivam Patel\Downloads\Scaling Vedic Quant Alpha Engine.md',
]

def clean_and_split(text):
    # Strip the standard markdown header
    text = re.sub(r'# Chat Conversation\n\nNote: _This is purely the output of the chat conversation and does not contain any raw data, codebase snippets, etc\. used to generate the output\._\n*', '', text)
    
    # Split by standard delimiters
    pattern = re.compile(r'(### User Input|### Planner Response|### Tool Call|\*User accepted|\*Checked command status|\*Viewed|\*Edited)')
    parts = pattern.split(text)
    
    blocks = []
    if parts[0].strip():
        blocks.append(parts[0].strip())
        
    for i in range(1, len(parts), 2):
        blocks.append((parts[i] + "\n\n" + parts[i+1]).strip())
        
    return [b for b in blocks if b]

all_blocks = []
for f in files:
    if not os.path.exists(f):
        print(f"MISSING: {f}")
        continue
        
    content = open(f, 'r', encoding='utf-8').read()
    blocks = clean_and_split(content)
    
    if not all_blocks:
        all_blocks.extend(blocks)
        continue
        
    # 1. Try exact suffix-prefix overlap
    max_overlap = 0
    search_range = min(len(blocks), len(all_blocks))
    for overlap in range(1, search_range + 1):
        if all_blocks[-overlap:] == blocks[:overlap]:
            max_overlap = overlap
            
    if max_overlap > 0:
        all_blocks.extend(blocks[max_overlap:])
    else:
        # 2. Try to find a branch point (overlap in the middle of all_blocks)
        branch_found = False
        # Search the first 5 blocks of the new file
        for i, b in enumerate(blocks[:5]):
            try:
                # Find the LAST occurrence of block 'b' in all_blocks
                idx = len(all_blocks) - 1 - all_blocks[::-1].index(b)
                
                # Check how many blocks match consecutively
                match_len = 0
                while idx + match_len < len(all_blocks) and i + match_len < len(blocks):
                    if all_blocks[idx + match_len] == blocks[i + match_len]:
                        match_len += 1
                    else:
                        break
                
                # If we matched at least 1 block, it's a branch point!
                if match_len > 0:
                    branch_found = True
                    # Truncate all_blocks up to the point of divergence
                    all_blocks = all_blocks[:idx + match_len]
                    # Append the rest of the new file
                    all_blocks.extend(blocks[i + match_len:])
                    break
            except ValueError:
                pass
                
        if not branch_found:
            # Absolute fallback, just append with a divider
            all_blocks.append('\n\n---\n\n')
            all_blocks.extend(blocks)

# Reconstruct the text
master_content = "# Chat Conversation\n\nNote: _This is purely the output of the chat conversation and does not contain any raw data, codebase snippets, etc. used to generate the output._\n\n"
master_content += "\n\n".join(all_blocks)

out_path = r'C:\Users\Shivam Patel\Downloads\master_chat_history.md'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(master_content)

print(f"Master chat history written to {out_path} with {len(all_blocks)} total blocks.")
