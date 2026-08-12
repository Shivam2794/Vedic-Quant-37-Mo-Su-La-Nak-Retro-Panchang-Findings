import os

file_path = r'E:\Python\Learn\Astrology 2-20260611T223423Z-3-001\Astrology 2\file_list.txt'

try:
    with open(file_path, 'r', encoding='utf-16le') as f:
        lines = [line.strip() for line in f if line.strip()]
except:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
    except:
        with open(file_path, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

out_dir = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch'

# split evenly
n = len(lines)
chunk_size = (n + 2) // 3
alpha_list = lines[:chunk_size]
beta_list = lines[chunk_size:2*chunk_size]
gamma_list = lines[2*chunk_size:]

with open(os.path.join(out_dir, 'alpha_files.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(alpha_list))
with open(os.path.join(out_dir, 'beta_files.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(beta_list))
with open(os.path.join(out_dir, 'gamma_files.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(gamma_list))

print(f"Total files: {n}")
print(f"Alpha: {len(alpha_list)}, Beta: {len(beta_list)}, Gamma: {len(gamma_list)}")
