#!/usr/bin/env python3
"""
OpenRouter chat-completion utility (hardened).

Design goals:
  * Zero unhandled exceptions -> always exits with a deterministic status code.
  * Never blocks forever: hard global deadline (default 45s) that is strictly
    below any external 60s watchdog, with per-request timeouts derived from the
    remaining budget.
  * API key resolution is layered (CLI > file > environment > embedded fallback)
    so the script is runnable out-of-the-box but overridable in production.
  * Secrets are never echoed in full.
  * No interactive/stdin blocking unless the user explicitly asks for it.

Exit codes:
  0 = success (model replied)
  1 = configuration error (no key)
  2 = network/timeout failure
  3 = HTTP/API error from OpenRouter
  4 = malformed response payload
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
except ImportError:  # pragma: no cover
    sys.stderr.write("DEPENDENCY ERROR: 'requests' is not installed. Run: pip install requests\n")
    sys.exit(2)


# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODELS_URL = "https://openrouter.ai/api/v1/models"

# Embedded fallback key (last-resort default; override via env/CLI in production).
EMBEDDED_API_KEY = (
    "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"
)

ENV_KEY_NAMES: Tuple[str, ...] = (
    "OPENROUTER_API_KEY",
    "OPENROUTER_KEY",
    "OPEN_ROUTER_API_KEY",
)

DEFAULT_MODEL = "anthropic/claude-opus-4.1"
# Ordered fallback chain: if a model id does not exist / is unavailable we walk down.
DEFAULT_MODEL_CHAIN: Tuple[str, ...] = (
    "anthropic/claude-opus-4.1",
    "anthropic/claude-sonnet-4",
    "anthropic/claude-3.5-sonnet",
)

DEFAULT_GLOBAL_DEADLINE = 45.0   # seconds, must stay < external 60s watchdog
MIN_REQUEST_TIMEOUT = 5.0        # never issue a request with less budget than this
CONNECT_TIMEOUT_CAP = 8.0
RETRYABLE_STATUS = {408, 409, 425, 429, 500, 502, 503, 504, 522, 524}


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def mask_secret(secret: str) -> str:
    """Return a log-safe representation of a secret."""
    if not secret:
        return "<empty>"
    s = secret.strip()
    if len(s) <= 12:
        return s[:2] + "*" * max(0, len(s) - 2)
    return f"{s[:10]}...{s[-4:]} (len={len(s)})"


def read_key_file(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                # Support "OPENROUTER_API_KEY=sk-or-..." style files.
                if "=" in line and line.split("=", 1)[0].strip().upper() in ENV_KEY_NAMES:
                    line = line.split("=", 1)[1].strip().strip("'\"")
                return line.strip().strip("'\"") or None
    except OSError as exc:
        sys.stderr.write(f"WARNING: cannot read key file {path!r}: {exc}\n")
    return None


def resolve_api_key(cli_key: Optional[str], key_file: Optional[str]) -> Tuple[Optional[str], str]:
    """Resolve the API key. Returns (key, source_description)."""
    # 1) explicit CLI argument
    if cli_key and cli_key.strip():
        return cli_key.strip(), "--api-key"

    # 2) explicit key file
    if key_file:
        k = read_key_file(key_file)
        if k:
            return k, f"--api-key-file {key_file}"

    # 3) environment variables
    for name in ENV_KEY_NAMES:
        v = os.environ.get(name)
        if v and v.strip():
            return v.strip(), f"env:{name}"

    # 4) conventional dotfiles
    for candidate in (
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "openrouter.key"),
        os.path.expanduser("~/.openrouter_key"),
        os.path.expanduser("~/.config/openrouter/key"),
    ):
        if os.path.isfile(candidate):
            k = read_key_file(candidate)
            if k:
                return k, f"file:{candidate}"

    # 5) embedded fallback (guaranteed non-empty -> script is always runnable)
    if EMBEDDED_API_KEY and EMBEDDED_API_KEY.strip():
        return EMBEDDED_API_KEY.strip(), "embedded-fallback"

    return None, "none"


class Deadline:
    """Monotonic global time budget."""

    def __init__(self, budget: float) -> None:
        self.budget = max(float(budget), MIN_REQUEST_TIMEOUT + 1.0)
        self.start = time.monotonic()

    def remaining(self) -> float:
        return self.budget - (time.monotonic() - self.start)

    def expired(self) -> bool:
        return self.remaining() <= 0.0

    def timeouts(self) -> Optional[Tuple[float, float]]:
        """(connect, read) timeouts sized to the remaining budget, or None if exhausted."""
        rem = self.remaining()
        if rem < MIN_REQUEST_TIMEOUT:
            return None
        connect = min(CONNECT_TIMEOUT_CAP, max(2.0, rem * 0.25))
        read = max(MIN_REQUEST_TIMEOUT - connect, rem - connect - 0.5)
        return (round(connect, 2), round(read, 2))


# ----------------------------------------------------------------------------
# Core API call
# ----------------------------------------------------------------------------

def build_headers(api_key: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost/quality-inspector",
        "X-Title": "Brutal Multipoint Quality Inspector",
    }


def extract_text(payload: Dict[str, Any]) -> Optional[str]:
    """Robustly pull assistant text out of an OpenRouter/OpenAI-shaped payload."""
    if not isinstance(payload, dict):
        return None
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    first = choices[0]
    if not isinstance(first, dict):
        return None

    msg = first.get("message")
    if isinstance(msg, dict):
        content = msg.get("content")
        if isinstance(content, str) and content.strip():
            return content
        if isinstance(content, list):  # multimodal content blocks
            parts: List[str] = []
            for block in content:
                if isinstance(block, dict):
                    t = block.get("text") or block.get("content")
                    if isinstance(t, str):
                        parts.append(t)
                elif isinstance(block, str):
                    parts.append(block)
            joined = "".join(parts).strip()
            if joined:
                return joined
        reasoning = msg.get("reasoning")
        if isinstance(reasoning, str) and reasoning.strip():
            return reasoning

    # Legacy completion shape
    txt = first.get("text")
    if isinstance(txt, str) and txt.strip():
        return txt
    return None


def post_once(
    session: "requests.Session",
    api_key: str,
    model: str,
    messages: List[Dict[str, str]],
    max_tokens: int,
    temperature: float,
    deadline: Deadline,
) -> Tuple[str, Any]:
    """
    Single HTTP attempt.
    Returns (status, detail) where status in
    {"ok", "retry", "bad_model", "auth", "http_error", "network", "timeout", "malformed"}.
    """
    tmo = deadline.timeouts()
    if tmo is None:
        return ("timeout", "global budget exhausted before request")

    body = {
        "model": model,
        "messages": messages,
        "stream": False,
        "max_tokens": int(max_tokens),
        "temperature": float(temperature),
    }

    try:
        resp = session.post(
            API_URL,
            headers=build_headers(api_key),
            data=json.dumps(body).encode("utf-8"),
            timeout=tmo,
        )
    except requests.exceptions.Timeout as exc:
        return ("timeout", f"request timeout after {tmo}: {exc}")
    except requests.exceptions.RequestException as exc:
        return ("network", f"network error: {exc}")

    status = resp.status_code

    try:
        payload = resp.json()
    except ValueError:
        payload = None

    if status == 200:
        if payload is None:
            return ("malformed", (resp.text or "")[:500])
        # OpenRouter can return a 200 with an embedded error object.
        err = payload.get("error") if isinstance(payload, dict) else None
        if isinstance(err, dict):
            msg = str(err.get("message", ""))
            code = err.get("code")
            if code in (404,) or "not a valid model" in msg.lower() or "no endpoints" in msg.lower():
                return ("bad_model", msg or "model unavailable")
            return ("http_error", f"code={code} message={msg}")
        text = extract_text(payload)
        if text is None:
            return ("malformed", json.dumps(payload)[:800])
        return ("ok", (text, payload))

    detail = ""
    if isinstance(payload, dict):
        err = payload.get("error")
        if isinstance(err, dict):
            detail = str(err.get("message", ""))
        elif err is not None:
            detail = str(err)
    if not detail:
        detail = (resp.text or "")[:500]

    if status in (401, 403):
        return ("auth", f"HTTP {status}: {detail}")
    if status == 404 or "not a valid model" in detail.lower() or "no endpoints" in detail.lower():
        return ("bad_model", f"HTTP {status}: {detail}")
    if status in RETRYABLE_STATUS:
        return ("retry", f"HTTP {status}: {detail}")
    return ("http_error", f"HTTP {status}: {detail}")


def call_openrouter(
    prompt: str,
    api_key: str,
    models: List[str],
    max_tokens: int = 512,
    temperature: float = 0.2,
    budget: float = DEFAULT_GLOBAL_DEADLINE,
    max_attempts_per_model: int = 2,
    system: Optional[str] = None,
    verbose: bool = True,
) -> Tuple[int, Optional[str]]:
    """
    Try each model in order, with bounded retries, all inside one global deadline.
    Returns (exit_code, reply_text).
    """
    deadline = Deadline(budget)

    messages: List[Dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    last_kind = "timeout"
    last_detail: Any = "no attempt made"

    session = requests.Session()
    session.trust_env = True
    try:
        for model in models:
            for attempt in range(1, max_attempts_per_model + 1):
                if deadline.expired() or deadline.timeouts() is None:
                    last_kind, last_detail = "timeout", "global time budget exhausted"
                    break

                if verbose:
                    sys.stderr.write(
                        f"[info] model={model} attempt={attempt}/{max_attempts_per_model} "
                        f"budget_left={deadline.remaining():.1f}s\n"
                    )
                    sys.stderr.flush()

                kind, detail = post_once(
                    session, api_key, model, messages, max_tokens, temperature, deadline
                )

                if kind == "ok":
                    text, payload = detail
                    if verbose:
                        usage = payload.get("usage") if isinstance(payload, dict) else None
                        served = payload.get("model") if isinstance(payload, dict) else None
                        sys.stderr.write(f"[info] success model={served or model} usage={usage}\n")
                        sys.stderr.flush()
                    return (0, text)

                last_kind, last_detail = kind, detail

                if kind in ("auth", "bad_model", "http_error", "malformed"):
                    # Not worth retrying the same model.
                    if verbose:
                        sys.stderr.write(f"[warn] {kind}: {detail}\n")
                    break

                # retry / network / timeout -> brief backoff if budget allows
                if attempt < max_attempts_per_model:
                    backoff = min(1.5 * attempt, max(0.0, deadline.remaining() - MIN_REQUEST_TIMEOUT))
                    if backoff <= 0:
                        last_kind, last_detail = "timeout", "no budget left for retry"
                        break
                    if verbose:
                        sys.stderr.write(f"[warn] {kind}: {detail} -> retry in {backoff:.1f}s\n")
                        sys.stderr.flush()
                    time.sleep(backoff)

            if last_kind == "auth":
                break  # a bad key will fail for every model
            if last_kind == "timeout":
                break
    finally:
        try:
            session.close()
        except Exception:
            pass

    code_map = {
        "auth": 3,
        "http_error": 3,
        "bad_model": 3,
        "malformed": 4,
        "network": 2,
        "timeout": 2,
        "retry": 2,
    }
    sys.stderr.write(f"FAILURE [{last_kind}]: {last_detail}\n")
    return (code_map.get(last_kind, 2), None)


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Send a prompt to an OpenRouter model with hard timeouts and safe key handling."
    )
    p.add_argument("prompt", nargs="*", help="Prompt text (default: a short connectivity probe).")
    p.add_argument("--api-key", default=None, help="API key (overrides everything else).")
    p.add_argument("--api-key-file", default=None, help="Path to a file containing the API key.")
    p.add_argument(
        "--model",
        default=None,
        help=f"Model id. Default chain: {', '.join(DEFAULT_MODEL_CHAIN)}",
    )
    p.add_argument(
        "--no-fallback",
        action="store_true",
        help="Do not try fallback models if the requested model is unavailable.",
    )
    p.add_argument("--system", default=None, help="Optional system prompt.")
    p.add_argument("--max-tokens", type=int, default=512, help="Max completion tokens (default 512).")
    p.add_argument("--temperature", type=float, default=0.2, help="Sampling temperature (default 0.2).")
    p.add_argument(
        "--budget",
        type=float,
        default=DEFAULT_GLOBAL_DEADLINE,
        help=f"Global wall-clock budget in seconds (default {DEFAULT_GLOBAL_DEADLINE:.0f}).",
    )
    p.add_argument("--attempts", type=int, default=2, help="Attempts per model (default 2).")
    p.add_argument("--json", action="store_true", help="Print result as JSON.")
    p.add_argument("--quiet", action="store_true", help="Suppress progress logs on stderr.")
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve config and exit without making any network call.",
    )
    args = p.parse_args(argv)

    # Sanitize numeric inputs (defensive: no negative/absurd values).
    args.max_tokens = max(1, min(int(args.max_tokens), 8192))
    args.temperature = min(max(float(args.temperature), 0.0), 2.0)
    args.budget = min(max(float(args.budget), MIN_REQUEST_TIMEOUT + 1.0), 55.0)
    args.attempts = max(1, min(int(args.attempts), 5))
    return args


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    verbose = not args.quiet

    prompt = " ".join(args.prompt).strip() if args.prompt else ""
    if not prompt:
        prompt = "Reply with exactly one short sentence confirming you are reachable."

    api_key, source = resolve_api_key(args.api_key, args.api_key_file)
    if not api_key:
        sys.stderr.write(
            "CONFIG ERROR: No API key found. Set OPENROUTER_API_KEY in your environment, e.g.\n"
            "  export OPENROUTER_API_KEY='sk-or-v1-...'\n"
            "or pass --api-key-file /path/to/key.txt\n"
        )
        return 1

    if args.model:
        models = [args.model] if args.no_fallback else (
            [args.model] + [m for m in DEFAULT_MODEL_CHAIN if m != args.model]
        )
    else:
        models = [DEFAULT_MODEL_CHAIN[0]] if args.no_fallback else list(DEFAULT_MODEL_CHAIN)

    if verbose:
        sys.stderr.write(
            f"[info] key source={source} key={mask_secret(api_key)}\n"
            f"[info] models={models} budget={args.budget:.0f}s "
            f"max_tokens={args.max_tokens} temperature={args.temperature}\n"
        )
        sys.stderr.flush()

    if args.dry_run:
        info = {
            "dry_run": True,
            "key_source": source,
            "key_preview": mask_secret(api_key),
            "models": models,
            "prompt_chars": len(prompt),
            "budget_seconds": args.budget,
        }
        print(json.dumps(info, indent=2))
        return 0

    t0 = time.monotonic()
    code, reply = call_openrouter(
        prompt=prompt,
        api_key=api_key,
        models=models,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        budget=args.budget,
        max_attempts_per_model=args.attempts,
        system=args.system,
        verbose=verbose,
    )
    elapsed = time.monotonic() - t0

    if code == 0 and reply is not None:
        if args.json:
            print(json.dumps({"ok": True, "elapsed_seconds": round(elapsed, 2), "reply": reply}, indent=2))
        else:
            print(reply.strip())
        if verbose:
            sys.stderr.write(f"[info] done in {elapsed:.2f}s\n")
        return 0

    if args.json:
        print(json.dumps({"ok": False, "elapsed_seconds": round(elapsed, 2), "exit_code": code}, indent=2))
    if verbose:
        sys.stderr.write(f"[info] failed after {elapsed:.2f}s (exit={code})\n")
    return code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.stderr.write("\nINTERRUPTED by user.\n")
        sys.exit(130)
    except Exception as exc:  # absolute last-resort guard
        sys.stderr.write(f"UNHANDLED ERROR: {type(exc).__name__}: {exc}\n")
        sys.exit(2)