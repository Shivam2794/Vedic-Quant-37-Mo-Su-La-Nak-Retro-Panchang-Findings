import json, re
html = open('skool_page.html', encoding='utf-8').read()
match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    
    def find_parent_with_key(obj, target_key, target_val=None):
        results = []
        if isinstance(obj, dict):
            if target_key in obj:
                if target_val is None or obj[target_key] == target_val:
                    results.append(obj)
            for k, v in obj.items():
                results.extend(find_parent_with_key(v, target_key, target_val))
        elif isinstance(obj, list):
            for item in obj:
                results.extend(find_parent_with_key(item, target_key, target_val))
        return results

    # The user is visiting a specific classroom module: 9f01d6ec68964cfdb215ca91058947d1
    # Let's find any object that contains videoId
    parents = find_parent_with_key(data, 'videoId')
    for p in parents:
        print(json.dumps(p, indent=2))
