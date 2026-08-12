import os
import asyncio
from dotenv import load_dotenv
load_dotenv()
from lightrag import QueryParam
from nadi_master_pipeline import NadiKnowledgeGraph

async def main():
    graph_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\nadi_sutras_memory"
    graph = NadiKnowledgeGraph(graph_dir)
    await graph._ensure_init()
    
    query_str = "What are the core sutras or rules related to debt, loss, money, or career mentioned in these books?"
    print(f"Querying graph with: '{query_str}'\n")
    
    # Use global search to explore entire memory and synthesize combinations
    result = await asyncio.to_thread(graph.rag.query, query_str, param=QueryParam(mode="global"))
    
    print("\n--- QUERY RESULT ---")
    print(result)
    print("--------------------")

if __name__ == "__main__":
    asyncio.run(main())
