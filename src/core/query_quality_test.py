import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from lightrag import LightRAG
from lightrag.utils import EmbeddingFunc
from sentence_transformers import SentenceTransformer
from openai import AsyncOpenAI

# Load the exact same embedding model used for graph construction
print("Loading BAAI/bge-m3...")
model = SentenceTransformer("BAAI/bge-m3")

async def _real_embed(texts):
    return await asyncio.to_thread(model.encode, texts)

openrouter_client = AsyncOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

async def _deepseek_v4_pro_extract(prompt, system_prompt=None, history_messages=[], **kwargs):
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if history_messages:
        messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    try:
        response = await openrouter_client.chat.completions.create(
            model="deepseek/deepseek-v4-pro",
            messages=messages,
            temperature=kwargs.get("temperature", 0.0),
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Query Error: {e}")
        return ""

def main():
    graph_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\nadi_sutras_memory"
    
    print("Connecting to Graph Memory...")
    rag = LightRAG(
        working_dir=graph_dir,
        llm_model_func=_deepseek_v4_pro_extract,
        llm_model_max_async=2,
        embedding_func=EmbeddingFunc(
            embedding_dim=1024,
            max_token_size=512,
            func=_real_embed,
        ),
    )
    
    query1 = "What specific combinations or yogas indicate massive wealth creation vs severe debt in these Nadi texts? Quote the planetary positions."
    print(f"\n--- QUERY ---\n{query1}\n")
    
    # We use global mode to force DeepSeek to synthesize across the entire graph
    result = rag.query(query1, param={"mode": "global"})
    
    print("\n--- RESULTS ---")
    print(result)

if __name__ == "__main__":
    main()
