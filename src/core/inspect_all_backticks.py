import os

downloads_dir = r"C:\Users\Shivam Patel\Downloads"
md_path = os.path.join(downloads_dir, "Synthesizing High-Accuracy Options Data 13.md")

with open(md_path, "r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f):
        if line.strip().startswith("```") or line.strip().startswith("````"):
            print(f"Line {i+1}: {repr(line)}")
