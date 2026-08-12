import json, re

path = r'C:\Users\Shivam Patel\.gemini\antigravity\brain\local_chat_entities.json'
out_path = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\secrets.txt'

try:
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    
    matches = re.finditer(r'.{0,100}PK[A-Z0-9]{15,}.{0,150}', text)
    
    with open(out_path, 'w', encoding='utf-8') as out_f:
        for m in matches:
            out_f.write(m.group(0) + '\n')
            
    print("Done")
except Exception as e:
    print('Error:', e)
