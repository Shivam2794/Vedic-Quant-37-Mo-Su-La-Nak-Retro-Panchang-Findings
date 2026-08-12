import os
import json
import requests
import time
from pathlib import Path

DEEPSEEK_API_KEY = "sk-8562d3b831364627bb812451d8da59b4"
URL = "https://api.deepseek.com/chat/completions"

# Input and output paths
SUMMARY_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\eff7bb86-675c-4bc8-9fa4-30cb849f8cfc\papers\summaries"
OUTPUT_FILE = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\879cc675-1bac-47f1-9b56-8c074e27bd91\brute_force_1000_phase_master_plan.md"

def get_deepseek_completion(prompt):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are the ultimate God-Tier AI Quant Architect. You are tasked with generating a 1000-phase Brute-Force Machine Learning Optimization Master Plan for a Vedic/Genesis trading strategy based on 175 academic papers."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 8000
    }
    
    for _ in range(3):
        try:
            response = requests.post(URL, headers=headers, json=data, timeout=300)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            print(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Request failed: {e}")
        time.sleep(5)
    return "FAILED TO GENERATE CONTENT."

def main():
    print("Loading 175-paper research summaries...")
    summaries = []
    for f in Path(SUMMARY_DIR).glob("*.md"):
        try:
            with open(f, 'r', encoding='utf-8') as file:
                content = file.read()
                summaries.append(f"--- PAPER: {f.name} ---\n{content}\n")
        except:
            pass

    print(f"Loaded {len(summaries)} summaries.")
    
    # We will chunk the summaries into 10 batches to give DeepSeek breathing room to output highly detailed phases.
    batch_size = len(summaries) // 10 + 1
    batches = [summaries[i:i + batch_size] for i in range(0, len(summaries), batch_size)]
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
        out.write("# 🌌 GOD-TIER GENESIS STRATEGY: 1000-PHASE BRUTE-FORCE ML OPTIMIZATION PLAN\n\n")
        out.write("> This master plan exhaustively applies the learnings from all 175 quantitative papers to the Vedic ML pipeline.\n\n")
    
    total_phases = 1000
    phases_per_batch = total_phases // len(batches)
    
    for i, batch in enumerate(batches):
        start_phase = (i * phases_per_batch) + 1
        end_phase = (i + 1) * phases_per_batch if i < len(batches) - 1 else total_phases
        
        print(f"Processing Batch {i+1}/{len(batches)} (Generating Phases {start_phase} to {end_phase})...")
        
        batch_text = "\n".join(batch)
        prompt = f"""
I am giving you a batch of academic paper summaries from our 175-paper database.
Your task is to extract every single quantitative concept, mathematical formula, feature engineering idea, and ML modeling technique from these papers.

Then, construct Phases {start_phase} to {end_phase} of our 1000-Phase Brute Force ML Master Plan.
Our baseline strategy is the "Genesis Strategy" (Vedic Quant features + XGBoost). We want to test every possible combination of features, labels, models, and execution algorithms.

Break down the insights from these specific papers into exhaustive, atomic, heavily detailed "Phases" numbered from {start_phase} to {end_phase}.
Format the output in clean Markdown. Be highly technical, quantitative, and explicit.

Here are the research summaries for this batch:
{batch_text}
        """
        
        result = get_deepseek_completion(prompt)
        
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as out:
            out.write(f"## BATCH {i+1} SYNTHESIS (Phases {start_phase}-{end_phase})\n\n")
            out.write(result + "\n\n")
            out.flush()
        
        print(f"Batch {i+1} written to master plan.")

if __name__ == "__main__":
    main()
