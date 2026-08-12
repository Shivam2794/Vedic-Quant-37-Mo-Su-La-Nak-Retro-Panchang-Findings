import os
import re

downloads_dir = r"C:\Users\Shivam Patel\Downloads"
md_path = os.path.join(downloads_dir, "Synthesizing High-Accuracy Options Data 13.md")

with open(md_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

# We want to find code blocks. Let's trace back where lines start with ```python or ```
blocks = []
in_block = False
current_block = []
start_line = 0

for i, line in enumerate(lines):
    if line.strip().startswith("```python"):
        in_block = True
        start_line = i
        current_block = []
    elif line.strip().startswith("```") and in_block:
        in_block = False
        blocks.append({
            "start": start_line,
            "end": i,
            "code": "".join(current_block),
            "context": "".join(lines[max(0, start_line-5):start_line])
        })
    elif in_block:
        current_block.append(line)

print(f"Found {len(blocks)} python code blocks.")
for idx, b in enumerate(blocks):
    print(f"\nBlock #{idx} (Lines {b['start']} to {b['end']}):")
    print("--- Context ---")
    print(b['context'])
    print("--- First 5 lines of code ---")
    print("".join(b['code'].splitlines()[:5]))
    print("-" * 40)
