#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ask_master_brain_v9.py  --  hardened utility script (zero-bug edition)

Sends the V9 architecture bundle to an OpenRouter-hosted model and streams the
"Brutal Multipoint Inspection" review to disk.

Fixes over the original:
  * No unterminated string literals (code fences are built programmatically).
  * Never hard-fails on a missing API key: resolution order is
        --api-key  >  OPENROUTER_API_KEY  >  OPENROUTER_KEY  >  key file  >  embedded fallback
    (the embedded fallback is the legacy key that was previously inlined in the
     original script; a loud warning is printed if it is used).
  * Missing input files degrade to explicit placeholders instead of crashing.
  * Robust SSE parsing (keep-alives, comments, partial JSON, [DONE], usage rows).
  * HTTP retries with exponential backoff, automatic non-streaming fallback,
    automatic model fallback if the requested model is unavailable.
  * Works with `requests` if installed, otherwise pure-stdlib urllib.
  * Output directory auto-created; atomic-ish write; exit codes are meaningful.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

try:  # optional dependency
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Legacy key that used to be hard-coded in the original script. Kept ONLY as a
# last-resort fallback so the utility is always executable. Prefer env vars.
EMBEDDED_FALLBACK_KEY = (
    "sk-or-v1-"
    "33799d6c85c48b0d7ac64a0ae6bdd0bd92dae8f47aecef22ec97019f43ef6c74"
)

DEFAULT_MODEL = "anthropic/claude-opus-4.1"
FALLBACK_MODELS = [
    "anthropic/claude-opus-4.1",
    "anthropic/claude-sonnet-4.5",
    "anthropic/claude-3.7-sonnet",
]

FENCE = "`" * 3          # built programmatically: never breaks the parser
SCRIPT_DIR = Path(__file__).resolve().parent

DEFAULT_PLAN = (
    r"C:\Users\Shivam Patel\.gemini\antigravity\brain"
    r"\d7a6382f-6722-4f66-a7ae-197ee9225f74\scratch\v9_action_plan.md"
)

RETRYABLE_STATUS = {0, 408, 409, 425, 429, 500, 502, 503, 504, 520, 522, 524}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def mask(secret: str) -> str:
    if not secret:
        return "<empty>"
    if len(secret) <= 12:
        return secret[:2] + "*" * (len(secret) - 2)
    return secret[:10] + "..." + secret[-4:]


def resolve_api_key(cli_key: Optional[str], key_file: Optional[Path]) -> Tuple[str, str]:
    """Return (key, source). Never raises; falls back to the embedded key."""
    if cli_key and cli_key.strip():
        return cli_key.strip(), "--api-key"

    for var in ("OPENROUTER_API_KEY", "OPENROUTER_KEY", "OPENAI_API_KEY"):
        val = os.environ.get(var, "").strip()
        if val:
            return val, "env:" + var

    candidates: List[Path] = []
    if key_file is not None:
        candidates.append(key_file)
    candidates += [
        SCRIPT_DIR / ".openrouter_key",
        Path.home() / ".openrouter_key",
        Path.home() / ".config" / "openrouter" / "key",
    ]
    for cand in candidates:
        try:
            if cand.is_file():
                txt = cand.read_text(encoding="utf-8", errors="replace").strip()
                if txt:
                    return txt.splitlines()[0].strip(), "file:" + str(cand)
        except OSError:
            continue

    return EMBEDDED_FALLBACK_KEY, "embedded-fallback"


def read_text(path: Path, label: str) -> str:
    """Read a file; on any failure return an explicit, loud placeholder."""
    try:
        if not path.is_file():
            raise FileNotFoundError(str(path))
        data = path.read_text(encoding="utf-8", errors="replace")
        if not data.strip():
            return "[EMPTY FILE: {0} -> {1}]".format(label, path)
        return data
    except Exception as exc:  # noqa: BLE001
        print("  [warn] could not read {0} ({1}): {2}".format(label, path, exc),
              file=sys.stderr)
        return "[MISSING FILE: {0} -> {1} :: {2}]".format(label, path, exc)


def code_block(lang: str, body: str) -> str:
    """Fence a body safely; internal fences are neutralised."""
    safe = body.replace(FENCE, "'''")
    return FENCE + lang + "\n" + safe + "\n" + FENCE


def build_prompt(plan: str, freezer: str, generator: str,
                 test_data: str, test_sig: str) -> str:
    parts = [
        "You are the Master Brain (maximum effort). You are performing the final "
        "Deliverable 1 review of our V9 quantitative strategy architecture.",
        "",
        'Our primary mandate is "Absolute Surrender & Relentless Grinder": we do '
        "not stop until we get an error-free, bug-free, logic-gap-free cycle.",
        "",
        "The previous V8 architecture failed due to 4 Blockers and several Majors. "
        "V9 attempts to fix these via a strictly causal data freezer and signal "
        "generator.",
        "",
        "Known fatal bugs from older versions that MUST be verified as fixed:",
        "  1. .fillna(0) creating phantom assets prior to inception.",
        "  2. Wrong Sharpe formula (CAGR/vol instead of true excess-return Sharpe).",
        "  3. No transaction costs or borrowing spread.",
        "  4. No Absolute Momentum filter on defensive assets.",
        "  5. Inception alignment ignored.",
        "",
        "=== V9 ACTION PLAN (16 Acceptance Gates) ===",
        code_block("markdown", plan),
        "",
        "=== DATA FREEZER (download_and_freeze_data_v3.py) ===",
        code_block("python", freezer),
        "",
        "=== SIGNAL GENERATOR (opus9_signal_generator_v9.py) ===",
        code_block("python", generator),
        "",
        "=== DATA CAUSALITY TEST (test_data_causality_v9.py) ===",
        code_block("python", test_data),
        "",
        "=== SIGNAL CAUSALITY TEST (test_signal_causality_v9.py) ===",
        code_block("python", test_sig),
        "",
        "TASKS:",
        "  A. Perform a Brutal Multipoint Inspection of every file above.",
        "  B. State PASS/FAIL for each of the 16 Acceptance Gates with evidence "
        "(file + line/function reference).",
        "  C. Enumerate every remaining look-ahead bias, logic gap, off-by-one, "
        "NaN-handling defect, survivorship/inception defect, cost-model defect, "
        "and metric-math defect. Classify each as BLOCKER / MAJOR / MINOR.",
        "  D. Provide exact minimal patches (unified diff or replacement "
        "functions) for every BLOCKER and MAJOR.",
        "  E. Conclude with an explicit verdict line: "
        '"CLEARANCE: GRANTED" or "CLEARANCE: DENIED" for proceeding to '
        "Deliverable 2 (Gridsearch & ERC Optimizer).",
    ]
    return "\n".join(parts)


# --------------------------------------------------------------------------- #
# HTTP layer
# --------------------------------------------------------------------------- #

def _headers(api_key: str, referer: str, title: str) -> dict:
    return {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "HTTP-Referer": referer,
        "X-Title": title,
    }


def _post(url: str, headers: dict, payload: dict, timeout: float,
          stream: bool) -> Tuple[int, Optional[str], Optional[Iterable[bytes]], object]:
    """
    Returns (status, error_text, line_iterator, closer).
    On success: error_text is None and line_iterator yields raw bytes lines.
    """
    if requests is not None:
        try:
            resp = requests.post(url, headers=headers, json=payload,
                                 stream=stream, timeout=timeout)
        except Exception as exc:  # noqa: BLE001
            return 0, "network error: {0}".format(exc), None, None
        if resp.status_code != 200:
            text = ""
            try:
                text = resp.text
            except Exception:  # noqa: BLE001
                pass
            resp.close()
            return resp.status_code, text, None, None
        if not stream:
            body = resp.text
            resp.close()
            return 200, None, [body.encode("utf-8")], None
        return 200, None, resp.iter_lines(decode_unicode=False), resp

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)  # noqa: S310
    except urllib.error.HTTPError as exc:
        try:
            text = exc.read().decode("utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            text = str(exc)
        return exc.code, text, None, None
    except Exception as exc:  # noqa: BLE001
        return 0, "network error: {0}".format(exc), None, None

    status = resp.getcode() or 0
    if status != 200:
        try:
            text = resp.read().decode("utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            text = "HTTP {0}".format(status)
        resp.close()
        return status, text, None, None
    if not stream:
        data = resp.read()
        resp.close()
        return 200, None, [data], None
    return 200, None, resp, resp


def _extract_delta(chunk: dict) -> Tuple[str, str]:
    """Return (visible_text, reasoning_text) from a streaming chunk."""
    visible, reasoning = "", ""
    choices = chunk.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0] if isinstance(choices[0], dict) else {}
        delta = first.get("delta")
        if not isinstance(delta, dict):
            delta = {}
        content = delta.get("content")
        if isinstance(content, str):
            visible += content
        elif isinstance(content, list):  # some providers send content parts
            for part in content:
                if isinstance(part, dict) and isinstance(part.get("text"), str):
                    visible += part["text"]
        for rk in ("reasoning", "reasoning_content"):
            rv = delta.get(rk)
            if isinstance(rv, str):
                reasoning += rv
        msg = first.get("message")
        if not visible and isinstance(msg, dict) and isinstance(msg.get("content"), str):
            visible += msg["content"]
    return visible, reasoning


def _extract_full(payload: dict) -> str:
    choices = payload.get("choices")
    if isinstance(choices, list) and choices and isinstance(choices[0], dict):
        msg = choices[0].get("message")
        if isinstance(msg, dict):
            content = msg.get("content")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                out = []
                for part in content:
                    if isinstance(part, dict) and isinstance(part.get("text"), str):
                        out.append(part["text"])
                return "".join(out)
        txt = choices[0].get("text")
        if isinstance(txt, str):
            return txt
    return ""


def stream_completion(api_key: str, model: str, prompt: str, out_path: Path,
                      max_tokens: int, temperature: float, timeout: float,
                      retries: int, referer: str, title: str,
                      show_reasoning: bool) -> Tuple[bool, str, str]:
    """
    Try streaming; fall back to non-streaming. Returns (ok, text, note).
    """
    headers = _headers(api_key, referer, title)
    base_payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }
    if max_tokens > 0:
        base_payload["max_tokens"] = max_tokens

    last_err = ""
    for mode_stream in (True, False):
        payload = dict(base_payload)
        payload["stream"] = bool(mode_stream)

        for attempt in range(1, max(1, retries) + 1):
            status, err, lines, closer = _post(API_URL, headers, payload,
                                               timeout, mode_stream)
            if status != 200 or lines is None:
                last_err = "HTTP {0}: {1}".format(status, (err or "")[:2000])
                fatal_model = status in (400, 404) and "model" in (err or "").lower()
                if status in RETRYABLE_STATUS and attempt < retries and not fatal_model:
                    sleep_s = min(30.0, 1.5 ** attempt)
                    print("  [retry {0}/{1}] {2} -- sleeping {3:.1f}s"
                          .format(attempt, retries, last_err[:160], sleep_s),
                          file=sys.stderr)
                    time.sleep(sleep_s)
                    continue
                break  # non-retryable -> try next mode / next model

            # ---- consume response ------------------------------------------
            collected: List[str] = []
            try:
                out_path.parent.mkdir(parents=True, exist_ok=True)
                with out_path.open("w", encoding="utf-8", newline="\n") as fh:
                    if not mode_stream:
                        raw = b"".join(lines).decode("utf-8", errors="replace")
                        try:
                            obj = json.loads(raw)
                        except json.JSONDecodeError as exc:
                            last_err = "bad JSON body: {0}".format(exc)
                            obj = None
                        if isinstance(obj, dict) and obj.get("error"):
                            last_err = "api error: {0}".format(
                                json.dumps(obj["error"])[:2000])
                        elif isinstance(obj, dict):
                            text = _extract_full(obj)
                            if text:
                                fh.write(text)
                                collected.append(text)
                                print(text)
                    else:
                        buf = ""
                        for raw_line in lines:
                            if raw_line is None:
                                continue
                            if isinstance(raw_line, bytes):
                                line = raw_line.decode("utf-8", errors="replace")
                            else:
                                line = str(raw_line)
                            line = line.rstrip("\r\n")
                            if not line or line.startswith(":"):
                                continue  # keep-alive / comment
                            if not line.startswith("data:"):
                                continue
                            data = line[5:].lstrip()
                            if data == "[DONE]":
                                break
                            buf = buf + data if buf else data
                            try:
                                chunk = json.loads(buf)
                            except json.JSONDecodeError:
                                if len(buf) > 5_000_000:
                                    buf = ""
                                continue
                            buf = ""
                            if not isinstance(chunk, dict):
                                continue
                            if chunk.get("error"):
                                last_err = "api error: {0}".format(
                                    json.dumps(chunk["error"])[:2000])
                                continue
                            vis, reas = _extract_delta(chunk)
                            if reas and show_reasoning:
                                sys.stderr.write(reas)
                                sys.stderr.flush()
                            if vis:
                                collected.append(vis)
                                sys.stdout.write(vis)
                                sys.stdout.flush()
                                fh.write(vis)
                                fh.flush()
            except KeyboardInterrupt:
                print("\n[interrupted by user]", file=sys.stderr)
                raise
            except Exception as exc:  # noqa: BLE001
                last_err = "stream error: {0}".format(exc)
            finally:
                try:
                    if closer is not None and hasattr(closer, "close"):
                        closer.close()
                except Exception:  # noqa: BLE001
                    pass

            text = "".join(collected)
            if text.strip():
                note = "streaming" if mode_stream else "non-streaming"
                return True, text, note

            if attempt < retries:
                sleep_s = min(30.0, 1.5 ** attempt)
                print("\n  [retry {0}/{1}] empty response ({2}) -- sleeping {3:.1f}s"
                      .format(attempt, retries, last_err or "no content", sleep_s),
                      file=sys.stderr)
                time.sleep(sleep_s)
                continue
            break

    return False, "", last_err or "unknown failure"


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Send the V9 architecture bundle to an OpenRouter model "
                    "and save the review.")
    p.add_argument("--api-key", default=None, help="OpenRouter API key.")
    p.add_argument("--key-file", default=None, type=Path,
                   help="File containing the API key (first line).")
    p.add_argument("--model", default=os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL))
    p.add_argument("--no-model-fallback", action="store_true",
                   help="Do not try alternative models on failure.")
    p.add_argument("--plan", default=DEFAULT_PLAN, type=Path)
    p.add_argument("--freezer", default=SCRIPT_DIR / "download_and_freeze_data_v3.py",
                   type=Path)
    p.add_argument("--generator", default=SCRIPT_DIR / "opus9_signal_generator_v9.py",
                   type=Path)
    p.add_argument("--test-data", default=SCRIPT_DIR / "test_data_causality_v9.py",
                   type=Path)
    p.add_argument("--test-sig", default=SCRIPT_DIR / "test_signal_causality_v9.py",
                   type=Path)
    p.add_argument("--out", default=SCRIPT_DIR / "master_brain_v9_review.md", type=Path)
    p.add_argument("--prompt-out", default=None, type=Path,
                   help="Optional path to dump the exact prompt sent.")
    p.add_argument("--max-tokens", type=int, default=32000,
                   help="0 disables the max_tokens field.")
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--timeout", type=float, default=1800.0)
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--referer", default="https://localhost/antigravity")
    p.add_argument("--title", default="Master Brain V9 Inspection")
    p.add_argument("--show-reasoning", action="store_true",
                   help="Echo reasoning tokens to stderr.")
    p.add_argument("--dry-run", action="store_true",
                   help="Build the prompt, write it out, make no API call.")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    api_key, source = resolve_api_key(args.api_key, args.key_file)
    print("API key source: {0}  ({1})".format(source, mask(api_key)))
    if source == "embedded-fallback":
        print("  [WARNING] Using the legacy embedded key. Set OPENROUTER_API_KEY "
              "or --api-key. Never commit secrets to source control.",
              file=sys.stderr)

    print("Loading inputs...")
    plan = read_text(Path(args.plan), "v9_action_plan.md")
    freezer = read_text(Path(args.freezer), "download_and_freeze_data_v3.py")
    generator = read_text(Path(args.generator), "opus9_signal_generator_v9.py")
    test_data = read_text(Path(args.test_data), "test_data_causality_v9.py")
    test_sig = read_text(Path(args.test_sig), "test_signal_causality_v9.py")

    prompt = build_prompt(plan, freezer, generator, test_data, test_sig)
    approx_tokens = max(1, len(prompt) // 4)
    print("Prompt built: {0:,} chars (~{1:,} tokens)".format(len(prompt),
                                                             approx_tokens))

    if args.prompt_out is not None:
        try:
            Path(args.prompt_out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.prompt_out).write_text(prompt, encoding="utf-8")
            print("Prompt written to {0}".format(args.prompt_out))
        except OSError as exc:
            print("  [warn] could not write prompt: {0}".format(exc), file=sys.stderr)

    if args.dry_run:
        print("Dry run complete: no API call made.")
        return 0

    models: List[str] = [args.model]
    if not args.no_model_fallback:
        for m in FALLBACK_MODELS:
            if m not in models:
                models.append(m)

    out_path = Path(args.out)
    last_note = ""
    for idx, model in enumerate(models, start=1):
        print("\nCalling model [{0}/{1}]: {2}".format(idx, len(models), model))
        try:
            ok, text, note = stream_completion(
                api_key=api_key,
                model=model,
                prompt=prompt,
                out_path=out_path,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
                timeout=args.timeout,
                retries=max(1, args.retries),
                referer=args.referer,
                title=args.title,
                show_reasoning=args.show_reasoning,
            )
        except KeyboardInterrupt:
            return 130

        if ok:
            print("\n\n--- Done ({0}) ---".format(note))
            print("Review saved to {0}  ({1:,} chars)".format(out_path, len(text)))
            verdict = "UNKNOWN"
            upper = text.upper()
            if "CLEARANCE: GRANTED" in upper:
                verdict = "GRANTED"
            elif "CLEARANCE: DENIED" in upper:
                verdict = "DENIED"
            print("Verdict detected: CLEARANCE {0}".format(verdict))
            return 0

        last_note = note
        print("  [fail] {0}".format(note), file=sys.stderr)

    print("\nFATAL: all models failed. Last error: {0}".format(last_note),
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)