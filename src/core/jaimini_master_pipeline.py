"""
jaimini_master_pipeline.py
===========================
Separate pipeline for Jaimini Astrology books.
Writes to jaimini_memory/ — completely isolated from the Nadi graph.

Models used:
  - LLM graph extraction:  deepseek/deepseek-v4-pro
  - Vision (charts/images): Seed 1.6 Flash (gatekeeper) + Qwen 3.6 35B (deep analysis)
"""

import os
import sys
import re
import asyncio
import logging
import base64
import requests
import time
import fitz  # PyMuPDF
import numpy as np

from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ─── Config ───────────────────────────────────────────────────────────────────
# DeepSeek Official API — separate from OpenRouter to enable parallel processing
DEEPSEEK_API_KEY = "sk-8562d3b831364627bb812451d8da59b4"
DEEPSEEK_URL     = "https://api.deepseek.com/chat/completions"
LLM_MODEL        = "deepseek-v4-pro"  # DeepSeek's official model name for V4 Pro

# OpenRouter key is only used by nadi_pdf_extractor for Vision (Seed 1.6 Flash + Qwen)
OR_API_KEY = "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"

SCRATCH  = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
GRAPH_DIR = os.path.join(SCRATCH, "jaimini_memory")  # SEPARATE from nadi_sutras_memory

BOOKS_DIR = r"C:\Users\Shivam Patel\Desktop\Python\Learn\Books\04_Vedic_Astrology_Gann_Theory"

ALL_BOOKS = [
    # Jaimini books ONLY — Nadi books are processed by nadi_master_pipeline.py
    os.path.join(BOOKS_DIR, "pdfcoffee.com_a-manual-of-jaimini-astrology-pdf-free.pdf"),
    os.path.join(BOOKS_DIR, "jaimini-astrology_compress.pdf"),
    os.path.join(BOOKS_DIR, "predicting-through-jaimini-chara-dasha.pdf"),
]

JAIMINI_INSTRUCTION = (
    "\n\nCRITICAL INSTRUCTION: You are processing JAIMINI ASTROLOGY texts. "
    "Focus on Jaimini-specific concepts: Chara Karakas (Atmakaraka, Amatyakaraka, etc.), "
    "Jaimini Aspects (sign aspects, not planetary aspects), Chara Dasha, Sthira Dasha, "
    "Karakamsha, Swamsha, Arudha Padas, Upapada, Darapada, and Jaimini Sutras. "
    "Also extract ALL rules related to money, wealth, career, loss, debt, "
    "poverty, financial gain, financial ruin, business, profession, and income. "
    "Tag these entities and relations with high-priority labels."
)

# ─── Helpers ─────────────────────────────────────────────────────────────────

def _deepseek_request(payload, timeout=240):
    """Send request directly to DeepSeek's official API (not OpenRouter)."""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    resp = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


# ─── PDF Extraction ──────────────────────────────────────────────────────────

def extract_book(pdf_path: str) -> str:
    """Extract text and image descriptions using the dual-model extractor."""
    import nadi_pdf_extractor
    book_name = os.path.basename(pdf_path)
    out_name = book_name.replace(".pdf", "_extracted.txt")
    out_path = os.path.join(SCRATCH, out_name)
    logger.info(f"Delegating extraction of {book_name} to nadi_pdf_extractor (Gatekeeper + Qwen)...")
    nadi_pdf_extractor.extract_pdf(pdf_path, out_path)
    return out_path


# ─── LightRAG LLM func ───────────────────────────────────────────────────────

async def _deepseek_v4_pro_extract(prompt: str, **kwargs) -> str:
    system_msg = kwargs.get("system_prompt") or "Extract entities and relationships."
    system_msg += JAIMINI_INSTRUCTION

    payload = {
        "model": LLM_MODEL,
        "temperature": 0.0,
        "top_p": 0.9,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": prompt},
        ],
    }

    MAX_RETRIES = 3
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = await asyncio.to_thread(_deepseek_request, payload, 240)

            # ── Safely extract content ──
            choice = r.get("choices", [{}])[0]
            msg = choice.get("message", {})
            content = msg.get("content") or msg.get("reasoning_content") or ""

            if not content or not content.strip():
                logger.warning(
                    f"Attempt {attempt}/{MAX_RETRIES}: API returned empty content. "
                    f"Raw keys in message: {list(msg.keys())}"
                )
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(2 * attempt)
                    continue
                else:
                    logger.error("All retries exhausted — returning empty extraction marker.")
                    return "-----\nentities\n-----"

            # ── Strip <think> blocks if present ──
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

            # ── Clean code fences ──
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # ── Only return if we got something meaningful ──
            if len(content) > 20:
                return content
            else:
                logger.warning(
                    f"Attempt {attempt}/{MAX_RETRIES}: Content too short ({len(content)} chars), retrying..."
                )
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(2 * attempt)
                    continue
                return content

        except requests.exceptions.Timeout:
            logger.warning(f"Attempt {attempt}/{MAX_RETRIES}: Request timed out.")
            if attempt < MAX_RETRIES:
                await asyncio.sleep(3 * attempt)
                continue
        except requests.exceptions.HTTPError as e:
            status = getattr(e.response, 'status_code', 'unknown')
            logger.warning(f"Attempt {attempt}/{MAX_RETRIES}: HTTP {status} error: {e}")
            if status == 429:  # rate limit
                await asyncio.sleep(10 * attempt)
            elif attempt < MAX_RETRIES:
                await asyncio.sleep(3 * attempt)
            if attempt == MAX_RETRIES:
                break
            continue
        except Exception as e:
            logger.error(f"Attempt {attempt}/{MAX_RETRIES}: Unexpected error: {type(e).__name__}: {e}")
            if attempt < MAX_RETRIES:
                await asyncio.sleep(2 * attempt)
                continue
            break

    logger.error("DeepSeek V4 Pro extraction failed after all retries.")
    return "-----\nentities\n-----"


from sentence_transformers import SentenceTransformer
# Initialize state-of-the-art MULTILINGUAL embedding model
embed_model = SentenceTransformer('BAAI/bge-m3')

async def _real_embed(texts: list) -> np.ndarray:
    """Real semantic embeddings for human-brain crosslinking."""
    embeddings = await asyncio.to_thread(embed_model.encode, texts)
    return embeddings

# ─── LightRAG Graph ──────────────────────────────────────────────────────────

class JaiminiKnowledgeGraph:
    def __init__(self, graph_dir: str):
        os.makedirs(graph_dir, exist_ok=True)
        self.rag = LightRAG(
            working_dir=graph_dir,
            llm_model_func=_deepseek_v4_pro_extract,
            llm_model_max_async=3,
            default_llm_timeout=3600,
            default_embedding_timeout=3600,
            embedding_func_max_async=1,
            embedding_batch_num=16,
            embedding_func=EmbeddingFunc(
                embedding_dim=1024,
                max_token_size=512,
                func=_real_embed,
            ),
        )
        self._init = False

    async def _ensure_init(self):
        if not self._init:
            await self.rag.initialize_storages()
            self._init = True

    async def ingest(self, text: str):
        await self._ensure_init()
        await self.rag.ainsert(text)

    async def query(self, q: str, mode="local") -> str:
        await self._ensure_init()
        return await self.rag.aquery(q, param=QueryParam(mode=mode))


# ─── Main ─────────────────────────────────────────────────────────────────────

async def main():
    logger.info(f"=== JAIMINI ASTROLOGY PIPELINE ===")
    logger.info(f"Using LLM: {LLM_MODEL}")
    logger.info(f"Graph dir: {GRAPH_DIR}")
    logger.info(f"Books to process: {len(ALL_BOOKS)}")

    graph = JaiminiKnowledgeGraph(GRAPH_DIR)

    for pdf_path in ALL_BOOKS:
        if not os.path.exists(pdf_path):
            logger.warning(f"SKIPPING (not found): {pdf_path}")
            continue

        book_name = os.path.basename(pdf_path)
        extracted_path = os.path.join(SCRATCH, book_name.replace(".pdf", "_extracted.txt"))

        # Skip vision re-extraction if text file already exists
        if os.path.exists(extracted_path) and os.path.getsize(extracted_path) > 1000:
            logger.info(f"Using cached extraction: {extracted_path} ({os.path.getsize(extracted_path):,} bytes)")
        else:
            extracted_path = extract_book(pdf_path)

        # Ingest into graph
        logger.info(f"Ingesting '{book_name}' into Jaimini LightRAG with {LLM_MODEL}...")
        with open(extracted_path, "r", encoding="utf-8") as f:
            content = f.read()

        t0 = time.time()
        await graph.ingest(content)
        elapsed = time.time() - t0
        logger.info(f"Ingested '{book_name}' in {elapsed:.1f}s")

    logger.info("=" * 60)
    logger.info("ALL JAIMINI BOOKS INGESTED. Running verification query...")
    result = await graph.query(
        "What are the Jaimini rules for career and wealth prediction using Chara Karakas and Arudha Padas?",
        mode="local"
    )
    print("\n===== JAIMINI CAREER/WEALTH QUERY RESULT =====")
    print(result)
    print("===============================================\n")
    logger.info("Jaimini pipeline complete.")


if __name__ == "__main__":
    asyncio.run(main())
