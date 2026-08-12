import json
import glob
import os

OUT_DIR = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\quant_rick_channel\The drivers of price and answers to them'

def plain_desc(raw):
    try:
        blob = json.loads(raw[4:] if raw.startswith('[v2]') else raw)
        parts = []
        def walk(node):
            if isinstance(node, dict):
                if node.get('type') == 'text':
                    parts.append(node.get('text', ''))
                for v in node.values():
                    if isinstance(v, (dict, list)):
                        walk(v)
            elif isinstance(node, list):
                for item in node:
                    walk(item)
        walk(blob)
        return ' '.join(parts).strip()
    except Exception:
        return raw

def find_v2(node, found):
    if isinstance(node, str) and node.startswith('[v2]'):
        found.append(node)
    elif isinstance(node, dict):
        for k, v in node.items():
            find_v2(v, found)
    elif isinstance(node, list):
        for item in node:
            find_v2(item, found)

for file in sorted(glob.glob(os.path.join(OUT_DIR, '*_metadata.json'))):
    if 'course_metadata' in file: continue
    
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    found = []
    find_v2(data, found)
    
    desc_txt = plain_desc(found[0]) if found else ''
    
    base = file.replace('_metadata.json', '')
    title = os.path.basename(base).split('_', 1)[1].replace('_', ' ')
    
    txt_file = base + '_description.txt'
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(f"{title}\n{'='*len(title)}\n\n{desc_txt}\n")
    
    print(f'Updated {os.path.basename(txt_file)}')
