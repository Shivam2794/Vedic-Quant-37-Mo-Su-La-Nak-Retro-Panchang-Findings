import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import requests

from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEY = "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"

async def _openrouter_extract(prompt: str, **kwargs) -> str:
    system_instruction = kwargs.get("system_prompt", "Extract entities and relationships as JSON.")
    
    financial_instruction = "\n\nCRITICAL INSTRUCTION: You must explicitly identify, extract, and connect all rules, principles, and sutras related to money, career, loss, debt, and finance. Do not omit any financial context. Track these as high-priority entities and relationships."
    system_instruction += financial_instruction

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek/deepseek-r1",
        "temperature": 0.0,
        "top_p": 0.9,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        def make_request():
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=180)
            response.raise_for_status()
            return response.json()
            
        r = await asyncio.to_thread(make_request)
        content = r["choices"][0]["message"]["content"]
        
        # Strip <think> tags from deepseek-r1 output
        import re
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        
        if content.startswith("```json"): content = content[7:]
        elif content.startswith("```"): content = content[3:]
        if content.endswith("```"): content = content[:-3]
        content = content.strip()
        
        if "<|COMPLETE|>" not in content and "{" not in content[:10]:
            content += "\n<|COMPLETE|>"
            
        return content
    except Exception as e:
        logger.error(f"OpenRouter extraction failed: {e}")
        return "-" * 5 + "\nentities\n----- "

async def _dummy_embed(texts: list) -> np.ndarray:
    return np.zeros((len(texts), 384), dtype=np.float32)

class NadiGraphMemory:
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
        self.rag_dir = os.path.join(workspace_dir, "nadi_sutras_memory")
        os.makedirs(self.rag_dir, exist_ok=True)

        self.rag = LightRAG(
            working_dir=self.rag_dir,
            llm_model_func=_openrouter_extract,
            llm_model_max_async=2,
            embedding_func=EmbeddingFunc(
                embedding_dim=384,
                max_token_size=512,
                func=_dummy_embed,
            ),
        )
        self._initialized = False

    async def _ensure_initialized(self):
        if not self._initialized:
            await self.rag.initialize_storages()
            self._initialized = True

    def insert_text(self, text_content: str):
        async def _insert():
            await self._ensure_initialized()
            await self.rag.ainsert(text_content)
        asyncio.run(_insert())

if __name__ == "__main__":
    import time
    
    workspace = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
    graph = NadiGraphMemory(workspace)
    
    if len(sys.argv) < 2:
        print("Usage: python ingester.py <file1.txt> <file2.txt> ...")
        sys.exit(1)
        
    for file_path in sys.argv[1:]:
        print(f"Loading {file_path}...")
        if not os.path.exists(file_path):
            print(f"Error: {file_path} not found.")
            continue
            
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        print(f"Loaded {len(content)} characters. Starting ingestion...")
        start_time = time.time()
        graph.insert_text(content)
        end_time = time.time()
        
        print(f"Ingestion complete for {file_path} in {end_time - start_time:.2f} seconds.")
    
    print("All tasks complete. Graph stored in:", graph.rag_dir)
