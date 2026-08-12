import sqlite3
uuids = ['064fe464-e3b5-4354-b219-8a1377b7fe51', '0c3658e3-764c-4355-8333-8644cc780dc9', '87510640-32b2-49d3-86ee-5a849fa10414', 'a0b2bfeb-e6c1-4b64-97e0-1fee9f09d6fa', 'a0f5c5d4-7eef-4b0e-bf59-718a07a15e98', 'c5e7376d-55f3-4de7-86d3-83943fb62e0e', 'e8be20ce-95ed-45f9-87e1-f6f0f572e0ea']
for u in uuids:
    db = f"C:/Users/Shivam Patel/.gemini/antigravity/conversations/{u}.db"
    try:
        conn = sqlite3.connect(db)
        meta = conn.execute("SELECT * FROM trajectory_meta").fetchone()
        title = meta[1] if meta and len(meta) > 1 else None 
        step = conn.execute("SELECT content FROM steps WHERE type='USER_INPUT' ORDER BY step_index ASC LIMIT 1").fetchone()
        prompt = step[0] if step else None
        print(f"UUID: {u}")
        print(f"Title: {title}")
        print(f"Prompt: {prompt[:300] if prompt else None}")
        print("-" * 40)
    except Exception as e:
        print(f"Error on {u}: {e}")
