"""
nadi_master_pipeline.py
========================
Full pipeline: extract text + charts/images from all Vedic/Jaimini Astrology PDFs,
then build a LightRAG knowledge graph using DeepSeek V4 Pro.

Models used:
  - LLM graph extraction:  deepseek/deepseek-v4-pro
  - Vision (charts/images): minimax/minimax-m2.7
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
# DeepSeek Official API — 75% discount on V4 Pro until May 31, 2026
DEEPSEEK_API_KEY = "sk-8562d3b831364627bb812451d8da59b4"
DEEPSEEK_URL     = "https://api.deepseek.com/chat/completions"
LLM_MODEL        = "deepseek-v4-pro"                   # DeepSeek V4 Pro (official)

# OpenRouter — used ONLY for Vision models (Seed 1.6 Flash gatekeeper + Qwen 35B deep analysis)
OR_API_KEY   = "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"
OR_URL       = "https://openrouter.ai/api/v1/chat/completions"
VISION_MODEL = "qwen/qwen3.6-35b-a3b"                 # Chart / figure vision (35B MoE, 3B active, vision=True, 262K ctx)

SCRATCH  = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
GRAPH_DIR = os.path.join(SCRATCH, "nadi_sutras_memory")

BOOKS_DIR = r"C:\Users\Shivam Patel\Desktop\Python\Learn\Books\04_Vedic_Astrology_Gann_Theory"

ALL_BOOKS = [
    # Nadi books ONLY — Jaimini books are processed by jaimini_master_pipeline.py
    os.path.join(BOOKS_DIR, "100 Nadi Sutras.pdf"),
    os.path.join(BOOKS_DIR, "Bhrigu Nandi Nadi - R.G. Rao.pdf"),
]

FINANCIAL_INSTRUCTION = (
    "\n\nCRITICAL INSTRUCTION: You must explicitly identify, extract, and connect "
    "ALL rules, principles, and sutras related to money, wealth, career, loss, debt, "
    "poverty, financial gain, financial ruin, business, profession, and income. "
    "Do NOT omit any financial or career-related context. "
    "Tag these entities and relations with high-priority labels."
)

# ─── Helpers ─────────────────────────────────────────────────────────────────

def _deepseek_request(payload, timeout=240):
    """Send request directly to DeepSeek's official API (V4 Pro, 75% off)."""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    resp = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=timeout)
    resp.raise_for_status()
    return resp.json()

def _or_request(payload, timeout=240):
    """Send request to OpenRouter (Vision models only)."""
    headers = {
        "Authorization": f"Bearer {OR_API_KEY}",
        "Content-Type": "application/json",
    }
    resp = requests.post(OR_URL, headers=headers, json=payload, timeout=timeout)
    resp.raise_for_status()
    return resp.json()

def describe_image(b64_image: str) -> str:
    """Send a chart/figure to Minimax M2.7 for description."""
    payload = {
        "model": VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "This is an image from a Vedic/Jaimini Astrology book. "
                            "Describe it in detail. If it is an astrological chart, list all "
                            "planets, their house positions, signs, and any noted aspects. "
                            "If it is a table or figure, transcribe and explain it fully. "
                            "Pay special attention to any indicators of wealth, career, debt, or loss."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"},
                    },
                ],
            }
        ],
    }
    try:
        r = _or_request(payload, timeout=60)
        return r["choices"][0]["message"]["content"]
    except Exception as e:
        logger.warning(f"Vision API failed: {e}")
        return "[Image/chart description unavailable]"


# ─── PDF Extraction ──────────────────────────────────────────────────────────

def extract_book(pdf_path: str) -> str:
    """Extract text and image descriptions from a single PDF using the dual-model extractor."""
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
    system_msg += FINANCIAL_INSTRUCTION

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
            # Some models put reasoning in 'reasoning_content' and leave 'content' as None
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
    # sentence-transformers encodes to numpy arrays directly
    embeddings = await asyncio.to_thread(embed_model.encode, texts)
    return embeddings

# ─── LightRAG Graph ──────────────────────────────────────────────────────────

class NadiKnowledgeGraph:
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
    logger.info(f"Using LLM: {LLM_MODEL}")
    logger.info(f"Using Vision: {VISION_MODEL}")
    logger.info(f"Graph dir: {GRAPH_DIR}")
    logger.info(f"Books to process: {len(ALL_BOOKS)}")

    graph = NadiKnowledgeGraph(GRAPH_DIR)

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
        logger.info(f"Ingesting '{book_name}' into LightRAG with {LLM_MODEL}...")
        with open(extracted_path, "r", encoding="utf-8") as f:
            content = f.read()

        t0 = time.time()
        await graph.ingest(content)
        elapsed = time.time() - t0
        logger.info(f"Ingested '{book_name}' in {elapsed:.1f}s")

    logger.info("=" * 60)
    logger.info("ALL BOOKS INGESTED. Running verification query...")
    result = await graph.query(
        "What are all rules and sutras related to money, wealth, debt, career, loss, or financial ruin?",
        mode="local"
    )
    print("\n===== FINANCIAL RULES QUERY RESULT =====")
    print(result)
    print("=========================================\n")
    logger.info("Pipeline complete.")


if __name__ == "__main__":
    asyncio.run(main())
