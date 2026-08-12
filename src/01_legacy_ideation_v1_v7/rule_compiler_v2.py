import sqlite3
import json
import os
import time
import requests
import re
from pathlib import Path

# --- Configuration ---
DEEPSEEK_API_KEY = "sk-8562d3b831364627bb812451d8da59b4"  # From previous session history
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

DB_PATH = Path(__file__).parent / "vedic_knowledge.db"
OUTPUT_RULES = Path(__file__).parent / "compiled_rules_v2.json"

BATCH_SIZE = 25  # Process 25 rules per API call
MAX_RETRIES = 3

SYSTEM_PROMPT = """You are the Antigravity Astrological Compiler.
Your job is to translate human-readable Vedic astrology rules into strict, executable Python code using the `pyswisseph` (Swiss Ephemeris) library.

You will receive a batch of rules. For each rule, you must output a JSON object containing:
1. `entity_name`: The exact entity name provided.
2. `category`: The category provided.
3. `python_code`: A pure python lambda function string that evaluates the rule. 
   - The function should take a single argument `ephem_data` (a dictionary of pre-computed planetary positions, houses, etc.) and return a boolean (True/False) or a float.
   - Example 1: `lambda ed: abs(ed['planets']['Sun']['lon'] - ed['planets']['Moon']['lon']) < 10.0`
   - Example 2: `lambda ed: ed['planets']['Jupiter']['house'] == 9`

Return ONLY a valid JSON array of these objects. No markdown, no explanation.
"""

def get_computable_entities():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT entity_name, category, description 
        FROM entities 
        WHERE is_computable = 1
    ''')
    rows = c.fetchall()
    conn.close()
    return [{"entity_name": r[0], "category": r[1], "description": r[2]} for r in rows]

def compile_batch(batch):
    prompt = "Translate the following rules:\n\n"
    for item in batch:
        prompt += f"Name: {item['entity_name']}\nCategory: {item['category']}\nDesc: {item['description']}\n---\n"

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            content = response.json()['choices'][0]['message']['content']
            
            # Extract JSON array from response
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            else:
                # DeepSeek might return an object with a "rules" key
                obj = json.loads(content)
                for v in obj.values():
                    if isinstance(v, list):
                        return v
                return []
                
        except Exception as e:
            print(f"Error on attempt {attempt+1}: {e}")
            time.sleep(2 ** attempt)
            
    print("Failed to compile batch.")
    return []

def main():
    print(f"Connecting to {DB_PATH}...")
    if not DB_PATH.exists():
        print("Database not found!")
        return

    entities = get_computable_entities()
    print(f"Found {len(entities)} computable entities to process.")
    
    # Load existing to resume if needed
    compiled_results = []
    if OUTPUT_RULES.exists():
        with open(OUTPUT_RULES, 'r') as f:
            compiled_results = json.load(f)
        print(f"Resuming with {len(compiled_results)} already compiled.")
        
    processed_names = {r['entity_name'] for r in compiled_results}
    remaining = [e for e in entities if e['entity_name'] not in processed_names]
    
    print(f"Remaining to compile: {len(remaining)}")
    
    batches_compiled = 0
    MAX_BATCHES = 10
    
    for i in range(0, len(remaining), BATCH_SIZE):
        if batches_compiled >= MAX_BATCHES:
            print(f"Reached MAX_BATCHES ({MAX_BATCHES}). Stopping compile run.")
            break
            
        batch = remaining[i:i+BATCH_SIZE]
        print(f"Processing batch {batches_compiled + 1} / {min(MAX_BATCHES, (len(remaining)//BATCH_SIZE) + 1)}...")
        
        results = compile_batch(batch)
        if results:
            compiled_results.extend(results)
            # Save incrementally
            with open(OUTPUT_RULES, 'w') as f:
                json.dump(compiled_results, f, indent=2)
            batches_compiled += 1
        else:
            print("Failed batch, pausing and retrying next...")
        
        time.sleep(1.0)  # Rate limiting


if __name__ == "__main__":
    main()
