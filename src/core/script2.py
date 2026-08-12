import os, ast

target_dir = r"E:\Python\Learn\Astrology 2-20260611T223423Z-3-001\Astrology 2\orion_essential"

summary = []
for root, dirs, files in os.walk(target_dir):
    for file in files:
        full_path = os.path.join(root, file)
        ext = os.path.splitext(file)[1].lower()
        if ext in ['.pyc', '.nbi', '.nbc', '.pt', '.pth', '.png', '.jsonl', '.log']:
            summary.append(f"- {file}: Binary/Log/Cache")
            continue
            
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f2:
                content = f2.read()
                
            if ext == '.py':
                try:
                    tree = ast.parse(content)
                    doc = ast.get_docstring(tree) or ""
                    doc_first = doc.split('\n')[0] if doc else "No docstring"
                    summary.append(f"- {file}: Python script. {doc_first}")
                except SyntaxError:
                    summary.append(f"- {file}: Python script (SyntaxError).")
            else:
                lines = content.splitlines()
                first_line = lines[0] if lines else ""
                summary.append(f"- {file}: {ext} file. {len(lines)} lines. {first_line[:50]}")
        except Exception as e:
            summary.append(f"- {file}: Error {str(e)}")

out_path = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\gamma_remaining_summary.txt'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(summary))

print(f"Done. Wrote {len(summary)} files to {out_path}")
