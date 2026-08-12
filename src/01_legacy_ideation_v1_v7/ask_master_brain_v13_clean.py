#!/usr/bin/env python3
"""
ask_master_brain_v13.py  --  Brutal Multipoint Quality Inspection request builder/sender.

Design rules enforced here:
  * NO hard-coded credentials anywhere (keys come from env var, key file, or --key-file).
  * Missing key is NOT a fatal condition: the script degrades gracefully to a dry run,
    writing the fully-rendered prompt to disk and exiting 0.
  * Every filesystem path is resolved/created safely; every network call is timed out
    and retried with exponential backoff on transient failures.
  * Deterministic, side-effect-free prompt construction (unit-testable via --dry-run).
"""

from __future__ import annotations

import argparse
import json
import os
import random
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

DEFAULT_SOURCE = "opus13_dual_momentum_gridsearch_v13.py"
DEFAULT_MODEL = "anthropic/claude-opus-4-1"
DEFAULT_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_OUT = "brutal_inspection_v13.md"
DEFAULT_TIMEOUT = 600.0
DEFAULT_RETRIES = 3
MAX_SOURCE_CHARS = 400_000
TRANSIENT_HTTP = frozenset({408, 409, 425, 429, 500, 502, 503, 504, 522, 524})

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_IO = 3
EXIT_NETWORK = 4
EXIT_RESPONSE = 5


# --------------------------------------------------------------------------- #
# logging helpers (stderr for diagnostics, stdout reserved for payload/paths)
# --------------------------------------------------------------------------- #
def log(level: str, msg: str) -> None:
    sys.stderr.write(f"[{level}] {msg}\n")
    sys.stderr.flush()


def die(level: str, msg: str, code: int) -> "None":
    log(level, msg)
    sys.exit(code)


# --------------------------------------------------------------------------- #
# credential resolution -- never from source code
# --------------------------------------------------------------------------- #
def read_key_file(path: Path) -> Optional[str]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        log("warn", f"cannot read key file {path}: {exc}")
        return None
    key = raw.strip()
    if not key:
        log("warn", f"key file {path} is empty")
        return None
    if "\n" in key or "\r" in key:
        key = key.splitlines()[0].strip()
    return key or None


def resolve_api_key(cli_key_file: Optional[str]) -> Tuple[Optional[str], str]:
    """Return (key, source_description). key is None when unavailable."""
    if cli_key_file:
        p = Path(cli_key_file).expanduser()
        key = read_key_file(p)
        if key:
            return key, f"--key-file {p}"
        return None, f"--key-file {p} (unusable)"

    env_file = os.environ.get("OPENROUTER_API_KEY_FILE", "").strip()
    if env_file:
        p = Path(env_file).expanduser()
        key = read_key_file(p)
        if key:
            return key, f"OPENROUTER_API_KEY_FILE={p}"

    for var in ("OPENROUTER_API_KEY", "OPENROUTER_TOKEN"):
        val = os.environ.get(var, "").strip()
        if val:
            return val, f"env:{var}"

    default_path = Path.home() / ".config" / "openrouter" / "api_key"
    if default_path.is_file():
        key = read_key_file(default_path)
        if key:
            return key, f"default:{default_path}"

    return None, "none"


def redact(key: str) -> str:
    if len(key) <= 8:
        return "*" * len(key)
    return f"{key[:4]}...{key[-4:]} (len={len(key)})"


# --------------------------------------------------------------------------- #
# prompt construction
# --------------------------------------------------------------------------- #
PROMPT_TEMPLATE = """Here is the V13 Python script for our trading strategy gridsearch.

The core engine has been rewritten to close the previously identified P0 defects:
  * cyclical coordinate descent for ERC weights (no closed-form approximation),
  * correct log/geometric compounding of returns,
  * hard inception masks (no .fillna(0) phantom assets before an asset's first print),
  * explicit transaction costs and a borrowing spread on any leverage/cash borrow,
  * absolute momentum gating applied to defensive assets as well as risk assets,
  * a single unified evaluation window across every candidate configuration,
  * true excess-return Sharpe (mean(excess)/std(excess) * sqrt(periods)), not CAGR/vol.

Reported results: {v12_sharpe} Sharpe on the V12 base, {v13_sharpe} Sharpe on the V13 \
Dual Momentum base.

Run the Brutal Multipoint Quality Inspection on V13 and answer precisely:

1. Enumerate every remaining mathematical error, off-by-one, lookahead leak, survivorship
   or inception-alignment gap, rebalance-timing bug, cost-model understatement, or
   statistical mis-specification. For each: file location, why it is wrong, the corrected
   formula/code, and the expected sign and magnitude of its impact on reported Sharpe.
2. Given zero lookahead and realistic costs, what is a defensible upper bound on the
   achievable Sharpe for this specific asset universe ({universe})? Show the reasoning
   (correlation structure, achievable diversification ratio, cost drag, turnover).
3. The stakeholder demands > {target_sharpe} Sharpe. Is universe expansion into
   genuinely uncorrelated return streams (managed futures / trend following, broad
   commodities, carry, short-vol-with-tail-hedge, cross-sectional FX) the only remaining
   lever, or are there in-universe levers (volatility targeting, risk-parity overlays,
   signal blending, rebalance-frequency optimisation) that survive out-of-sample scrutiny?
   Be explicit about which proposals are overfitting risks.

Answer as a rigorous quantitative reviewer. Do not flatter. If a claimed fix is
incomplete, say so and show the counterexample.

<v13_code path="{src_path}" chars="{src_chars}">
{code}
</v13_code>
"""


def load_source(path: Path) -> str:
    if not path.exists():
        die("fatal:io", f"source file not found: {path}", EXIT_IO)
    if not path.is_file():
        die("fatal:io", f"source path is not a regular file: {path}", EXIT_IO)
    try:
        code = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        die("fatal:io", f"cannot read source {path}: {exc}", EXIT_IO)
        return ""  # unreachable
    if not code.strip():
        die("fatal:io", f"source file is empty: {path}", EXIT_IO)
    if len(code) > MAX_SOURCE_CHARS:
        log(
            "warn",
            f"source {len(code)} chars exceeds cap {MAX_SOURCE_CHARS}; truncating tail",
        )
        code = code[:MAX_SOURCE_CHARS] + "\n# ...[TRUNCATED FOR PROMPT LENGTH]...\n"
    return code


def build_prompt(args: argparse.Namespace, src_path: Path, code: str) -> str:
    return PROMPT_TEMPLATE.format(
        v12_sharpe=f"{args.v12_sharpe:.2f}",
        v13_sharpe=f"{args.v13_sharpe:.2f}",
        universe=args.universe,
        target_sharpe=f"{args.target_sharpe:.2f}",
        src_path=src_path.as_posix(),
        src_chars=len(code),
        code=code,
    )


def build_payload(args: argparse.Namespace, prompt: str) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "model": args.model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": args.temperature,
    }
    if args.max_tokens > 0:
        payload["max_tokens"] = args.max_tokens
    return payload


# --------------------------------------------------------------------------- #
# output helpers
# --------------------------------------------------------------------------- #
def write_text(path: Path, text: str) -> Path:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8", newline="\n")
        os.replace(tmp, path)
    except OSError as exc:
        die("fatal:io", f"cannot write {path}: {exc}", EXIT_IO)
    return path


# --------------------------------------------------------------------------- #
# network
# --------------------------------------------------------------------------- #
def post_json(
    endpoint: str,
    payload: Dict[str, Any],
    api_key: str,
    timeout: float,
    retries: int,
    referer: Optional[str],
    title: Optional[str],
) -> Dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "brutal-inspector/13.1",
    }
    if referer:
        headers["HTTP-Referer"] = referer
    if title:
        headers["X-Title"] = title

    context = ssl.create_default_context()
    attempts = max(1, retries)
    last_err = "unknown error"

    for attempt in range(1, attempts + 1):
        req = urllib.request.Request(endpoint, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=context) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
            try:
                return json.loads(raw)
            except json.JSONDecodeError as exc:
                die(
                    "fatal:response",
                    f"non-JSON response ({exc}); first 500 chars: {raw[:500]!r}",
                    EXIT_RESPONSE,
                )
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                detail = exc.read().decode("utf-8", errors="replace")[:800]
            except Exception:  # noqa: BLE001 - diagnostics only
                pass
            last_err = f"HTTP {exc.code} {exc.reason}: {detail}"
            if exc.code in (401, 403):
                die("fatal:auth", f"authentication rejected -> {last_err}", EXIT_NETWORK)
            if exc.code not in TRANSIENT_HTTP or attempt == attempts:
                die("fatal:http", last_err, EXIT_NETWORK)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_err = f"network error: {exc}"
            if attempt == attempts:
                die("fatal:network", last_err, EXIT_NETWORK)

        backoff = min(60.0, (2.0 ** (attempt - 1)) * 2.0) + random.uniform(0, 1.0)
        log("retry", f"attempt {attempt}/{attempts} failed ({last_err}); sleep {backoff:.1f}s")
        time.sleep(backoff)

    die("fatal:network", last_err, EXIT_NETWORK)
    return {}  # unreachable


def extract_content(result: Dict[str, Any]) -> str:
    if not isinstance(result, dict):
        die("fatal:response", "response is not a JSON object", EXIT_RESPONSE)

    err = result.get("error")
    if err:
        msg = err.get("message") if isinstance(err, dict) else str(err)
        die("fatal:api", f"provider returned error: {msg}", EXIT_RESPONSE)

    choices = result.get("choices")
    if not isinstance(choices, list) or not choices:
        die("fatal:response", f"no choices in response: {json.dumps(result)[:500]}", EXIT_RESPONSE)

    first = choices[0]
    if not isinstance(first, dict):
        die("fatal:response", "choices[0] is not an object", EXIT_RESPONSE)

    message = first.get("message")
    content: Any = None
    if isinstance(message, dict):
        content = message.get("content")
    if content is None:
        content = first.get("text")

    # Some providers return content as a list of typed parts.
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict):
                parts.append(str(part.get("text", "")))
            else:
                parts.append(str(part))
        content = "".join(parts)

    if not isinstance(content, str) or not content.strip():
        die(
            "fatal:response",
            f"empty content (finish_reason={first.get('finish_reason')!r})",
            EXIT_RESPONSE,
        )
    return content


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def parse_args(argv: Optional[list] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="ask_master_brain_v13",
        description="Send the V13 strategy source for Brutal Multipoint Quality Inspection.",
    )
    p.add_argument("--source", default=os.environ.get("V13_SOURCE", DEFAULT_SOURCE),
                   help="path to the V13 strategy script to inspect")
    p.add_argument("--out", default=os.environ.get("V13_OUT", DEFAULT_OUT),
                   help="path for the inspection markdown report")
    p.add_argument("--prompt-out", default=None,
                   help="path to also save the rendered prompt (default: <out>.prompt.txt)")
    p.add_argument("--model", default=os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL))
    p.add_argument("--endpoint", default=os.environ.get("OPENROUTER_ENDPOINT", DEFAULT_ENDPOINT))
    p.add_argument("--key-file", default=None,
                   help="file containing the API key (one line). Never hard-code keys.")
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    p.add_argument("--retries", type=int, default=DEFAULT_RETRIES)
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--max-tokens", type=int, default=0, help="0 = provider default")
    p.add_argument("--universe", default="SPY/QQQ/TLT/GLD/IEF/SHY")
    p.add_argument("--v12-sharpe", type=float, default=0.89)
    p.add_argument("--v13-sharpe", type=float, default=0.81)
    p.add_argument("--target-sharpe", type=float, default=1.20)
    p.add_argument("--referer", default=os.environ.get("OPENROUTER_REFERER"))
    p.add_argument("--title", default=os.environ.get("OPENROUTER_TITLE", "Brutal Inspection V13"))
    p.add_argument("--dry-run", action="store_true",
                   help="build and save the prompt only; make no network call")
    p.add_argument("--print-prompt", action="store_true",
                   help="echo the rendered prompt to stdout")

    args = p.parse_args(argv)

    if args.timeout <= 0:
        die("fatal:usage", "--timeout must be > 0", EXIT_USAGE)
    if args.retries < 1:
        die("fatal:usage", "--retries must be >= 1", EXIT_USAGE)
    if not (0.0 <= args.temperature <= 2.0):
        die("fatal:usage", "--temperature must be in [0, 2]", EXIT_USAGE)
    if args.max_tokens < 0:
        die("fatal:usage", "--max-tokens must be >= 0", EXIT_USAGE)
    return args


def main(argv: Optional[list] = None) -> int:
    args = parse_args(argv)

    src_path = Path(args.source).expanduser()
    code = load_source(src_path)
    prompt = build_prompt(args, src_path, code)
    payload = build_payload(args, prompt)

    out_path = Path(args.out).expanduser()
    prompt_path = (
        Path(args.prompt_out).expanduser()
        if args.prompt_out
        else out_path.with_name(out_path.name + ".prompt.txt")
    )

    log("info", f"source={src_path} chars={len(code)} prompt_chars={len(prompt)}")
    if args.print_prompt:
        sys.stdout.write(prompt)
        sys.stdout.write("\n")

    api_key, key_src = resolve_api_key(args.key_file)

    # No key is NOT fatal: degrade to a fully-usable offline artifact.
    if args.dry_run or api_key is None:
        write_text(prompt_path, prompt)
        if args.dry_run:
            log("info", f"dry-run: prompt written to {prompt_path}")
        else:
            log("info",
                "no API key found (checked --key-file, OPENROUTER_API_KEY_FILE, "
                "OPENROUTER_API_KEY, ~/.config/openrouter/api_key). "
                "Keys must never be hard-coded in source.")
            log("info", f"offline mode: prompt written to {prompt_path}; no request sent.")
        write_text(
            out_path,
            "# Brutal Inspection V13 - PENDING\n\n"
            f"- model (planned): `{args.model}`\n"
            f"- endpoint (planned): `{args.endpoint}`\n"
            f"- source: `{src_path.as_posix()}` ({len(code)} chars)\n"
            f"- prompt artifact: `{prompt_path.as_posix()}` ({len(prompt)} chars)\n\n"
            "No API key was available, so no model call was made. Provide a key via\n"
            "`OPENROUTER_API_KEY`, `OPENROUTER_API_KEY_FILE`, or `--key-file <path>`\n"
            "and re-run to populate this report.\n",
        )
        log("info", f"placeholder report written to {out_path}")
        return EXIT_OK

    log("info", f"key source={key_src} key={redact(api_key)}")
    log("info", f"POST {args.endpoint} model={args.model} timeout={args.timeout:.0f}s")

    result = post_json(
        endpoint=args.endpoint,
        payload=payload,
        api_key=api_key,
        timeout=args.timeout,
        retries=args.retries,
        referer=args.referer,
        title=args.title,
    )

    content = extract_content(result)
    write_text(out_path, content if content.endswith("\n") else content + "\n")

    usage = result.get("usage") if isinstance(result.get("usage"), dict) else {}
    log(
        "info",
        "usage prompt={} completion={} total={}".format(
            usage.get("prompt_tokens", "?"),
            usage.get("completion_tokens", "?"),
            usage.get("total_tokens", "?"),
        ),
    )
    log("info", f"saved report ({len(content)} chars) to {out_path}")
    print(out_path.as_posix())
    return EXIT_OK


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        die("fatal:interrupt", "interrupted by user", 130)