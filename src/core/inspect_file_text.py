import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

downloads_dir = r"C:\Users\Shivam Patel\Downloads"
md_path = os.path.join(downloads_dir, "Synthesizing High-Accuracy Options Data 13.md")

with open(md_path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Let's find occurrences of "def " and print 100 characters around them
matches = [m.start() for m in re.finditer(r"\bdef\b", content)]
print(f"Found {len(matches)} occurrences of 'def'.")
for idx, m in enumerate(matches[:10]):
    print(f"Match #{idx}:")
    print(content[max(0, m-50):min(len(content), m+150)])
    print("-" * 50)
