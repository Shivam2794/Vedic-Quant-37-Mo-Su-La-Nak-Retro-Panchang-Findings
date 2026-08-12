import os
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

downloads_dir = r"C:\Users\Shivam Patel\Downloads"
files_to_scan = [
    "Scaling Vedic Neural Pipeline.md",
    "Synthesizing High-Accuracy Options Data 13.md",
    "Synthesizing High-Accuracy Options Data 12.md",
    "Synthesizing High-Accuracy Options Data 11.md",
    "Synthesizing High-Accuracy Options Data 2.md",
    "Synthesizing High-Accuracy Options Data.md"
]

def find_python_blocks(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Let's search for python code blocks using a regex that handles backticks
    # Markdown code blocks start with ```python and end with ```
    # Sometimes they start with ````python and end with ````
    blocks = []
    # Find all occurrences of ```python ... ```
    # We use non-greedy matching. Since there can be newlines, we use re.DOTALL.
    pattern = r"```(?:python)?\n(.*?)\n```"
    matches = re.finditer(pattern, content, re.DOTALL)
    for m in matches:
        code = m.group(1)
        # Let's get some context (say, 200 characters before the block)
        start_idx = m.start()
        context_start = max(0, start_idx - 150)
        context = content[context_start:start_idx]
        blocks.append((code, context))
    return blocks

for fn in files_to_scan:
    fp = os.path.join(downloads_dir, fn)
    if not os.path.exists(fp):
        continue
    blocks = find_python_blocks(fp)
    print(f"\nFile: {fn} -> Found {len(blocks)} code blocks.")
    for idx, (code, context) in enumerate(blocks):
        print(f"  Block #{idx}: size={len(code)} characters")
        print("  Context:")
        print("    " + "\n    ".join(context.strip().splitlines()[-3:]))
        print("  Code head:")
        print("    " + "\n    ".join(code.splitlines()[:4]))
        print("-" * 30)
