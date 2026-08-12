import json
with open('all_courses_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
rd = data.get('props', {}).get('pageProps', {}).get('renderData', {})

def find_courses(node):
    if isinstance(node, dict):
        if node.get('unitType') == 'course' and 'id' in node and 'name' in node:
            meta = node.get('metadata', {})
            print(f"- {node.get('name')}: {meta.get('title')}")
        for k, v in node.items():
            find_courses(v)
    elif isinstance(node, list):
        for i in node:
            find_courses(i)
            
find_courses(rd)
