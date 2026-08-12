import os
import re

def check_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    issues = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        clean_line = line.strip()
        if clean_line.startswith('#'):
            continue
            
        # 1. Log(0) traps
        if re.search(r'\b(np|math|torch)\.log(10|2)?\(', clean_line):
            if 'clip' not in clean_line and '1e-' not in clean_line and '+1' not in clean_line.replace(' ', '') and '+ 1' not in clean_line:
                issues.append(f"Line {i+1} [Log(0) Trap]: {clean_line}")
                
        # 2. Exp overflow/NaN traps
        if re.search(r'\b(np|math|torch)\.exp\(', clean_line):
            if 'clip' not in clean_line and 'clamp' not in clean_line and '1e-' not in clean_line:
                issues.append(f"Line {i+1} [Exp NaN Trap]: {clean_line}")
                
        # 3. Sigmoid NaN propagation
        if '1 / (1 + ' in clean_line and 'exp(' in clean_line:
             if 'clip' not in clean_line and 'clamp' not in clean_line:
                 issues.append(f"Line {i+1} [Sigmoid NaN Propagation]: {clean_line}")
                 
        # 4. Division without smoothing
        # Find cases like df['A'] / df['B'] or a / b, but exclude file paths or URLs
        if '/' in clean_line:
            # check if it's a mathematical division (vars surrounded by space or parenthesis)
            if re.search(r'[\]\w\)]\s*/\s*[\[\w\(]', clean_line):
                # if there is no small epsilon added to denom, flag it
                if '1e-' not in clean_line and 'eps' not in clean_line.lower() and 'max(' not in clean_line:
                    # filter out common false positives like dates, html, etc.
                    if 'http' not in clean_line and '<' not in clean_line:
                        # try to narrow down to ML/Data logic
                        if 'df[' in clean_line or 'np.' in clean_line or 'torch.' in clean_line or 'tensor' in clean_line.lower():
                            issues.append(f"Line {i+1} [Div by Zero]: {clean_line}")

        # 5. Array dimension mismatches
        if re.search(r'\b(reshape|view|unsqueeze|squeeze)\(', clean_line):
            if '-1' not in clean_line: # -1 is safeish sometimes, but we can flag them all if we want. Let's just flag hardcoded ones
                issues.append(f"Line {i+1} [Hardcoded Shape Trap]: {clean_line}")
                
        if re.search(r'\b(np|torch)\.(cat|concatenate)\(', clean_line):
            issues.append(f"Line {i+1} [Concat Dim Mismatch Risk]: {clean_line}")

    return issues

def main():
    base_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
    exclude_dirs = ['__pycache__', 'nadi_env', 'nadi_env_backup', 'venv', '.git', 'site-packages']
    
    total_issues = 0
    with open("edge_case_report.txt", "w", encoding="utf-8") as out:
        for root, dirs, files in os.walk(base_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if file.endswith('.py') and file != 'edge_case_grinder.py':
                    filepath = os.path.join(root, file)
                    issues = check_file(filepath)
                    if issues:
                        out.write(f"--- File: {os.path.relpath(filepath, base_dir)} ---\n")
                        for issue in issues:
                            out.write(f"{issue}\n")
                            total_issues += 1
                        out.write("\n")
    print(f"Total issues found: {total_issues}")

if __name__ == "__main__":
    main()
