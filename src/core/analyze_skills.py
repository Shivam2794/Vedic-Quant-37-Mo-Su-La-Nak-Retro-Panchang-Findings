import json

index_path = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\antigravity-awesome-skills\skills_index.json'
with open(index_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find high-leverage meta-skills
keywords = ['antigravity', 'autonomous', 'context', 'memory', 'accuracy', 'speed', 'moyu', 'prompt', 'agent', 'recall']
high_value = []

for skill in data:
    desc = skill.get('description', '').lower()
    tags = [t.lower() for t in skill.get('tags', [])]
    name = skill.get('name', '').lower()
    
    # score based on keywords
    score = sum(1 for k in keywords if k in desc or k in name or any(k in t for t in tags))
    if score > 0:
        high_value.append((score, skill))

high_value.sort(key=lambda x: x[0], reverse=True)

with open(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\results.txt', 'w', encoding='utf-8') as out:
    out.write("Top Meta Skills for Antigravity:\n")
    for s, skill in high_value[:30]:
        out.write(f"- {skill.get('name')}: {skill.get('description')}\n")
