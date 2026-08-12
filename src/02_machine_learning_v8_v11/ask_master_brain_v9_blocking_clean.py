#!/usr/bin/env python3
"""
ask_master_brain_review.py
==========================

Utility script: assemble a "Brutal Multipoint Inspection" review prompt from a
set of local source/plan files and (optionally) submit it to an OpenRouter
chat-completions endpoint, saving the reply to disk.

Design rules enforced here
--------------------------
1. NO hard-coded secrets.  The API key is resolved, in priority order, from:
       a) --api-key <key>                (explicit, discouraged: shell history)
       b) --api-key-file <path>          (file containing only the key)
       c) $OPENROUTER_API_KEY            (environment variable)
       d) $OPENROUTER_API_KEY_FILE       (path in env var)
       e) ~/.config/openrouter/api_key   (conventional default location)
2. Absence of a key is NOT fatal.  The script degrades gracefully into
   --dry-run mode: the fully rendered prompt is written to disk, a clear notice
   is printed, and the process exits 0.  A key is only *required* when the user
   explicitly asks to send (--send) a request.
3. Missing input files are NOT fatal: a visible placeholder block is inserted so
   the reviewer can see exactly what was unavailable.
4. All network I/O has explicit timeouts, bounded retries with exponential
   backoff + jitter, and honours Retry-After on 429/503.
5. Secrets are never logged; any accidental occurrence is redacted.
6. File writes are atomic (temp file + os.replace) so a crash cannot leave a
   half-written artefact.

The script is fully executable with zero third-party dependencies in dry-run
mode; `requests` is imported lazily and only needed for --send.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

DEFAULT_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "anthropic/claude-3.5-sonnet"
DEFAULT_TIMEOUT = 180.0          # seconds, per HTTP attempt
DEFAULT_MAX_RETRIES = 4
DEFAULT_MAX_FILE_BYTES = 400_000  # per-file soft cap before truncation
DEFAULT_MAX_PROMPT_BYTES = 3_000_000  # total prompt hard cap
RETRYABLE_STATUS = frozenset({408, 409, 425, 429, 500, 502, 503, 504})
KEY_ENV_VAR = "OPENROUTER_API_KEY"
KEY_FILE_ENV_VAR = "OPENROUTER_API_KEY_FILE"
DEFAULT_KEY_PATH = Path.home() / ".config" / "openrouter" / "api_key"
SECRET_PATTERN = re.compile(r"sk-[A-Za-z0-9\-_]{8,}")


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #

def log(msg: str) -> None:
    """Print to stderr (stdout stays reserved for the model output)."""
    print(redact(msg), file=sys.stderr, flush=True)


def redact(text: str) -> str:
    """Mask anything that looks like an API key."""
    return SECRET_PATTERN.sub("sk-***REDACTED***", text)


def human_bytes(n: int) -> str:
    step = 1024.0
    val = float(n)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if val < step or unit == "GiB":
            return f"{val:.1f} {unit}" if unit != "B" else f"{int(val)} B"
        val /= step
    return f"{val:.1f} GiB"


def atomic_write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    """Write `text` to `path` atomically, creating parent dirs as needed."""
    path = Path(path)
    parent = path.parent if str(path.parent) else Path(".")
    parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(parent)
    )
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding=encoding, newline="\n") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass
        raise


# --------------------------------------------------------------------------- #
# API-key resolution (no secrets in source)
# --------------------------------------------------------------------------- #

def _read_key_file(path: Path) -> Optional[str]:
    try:
        raw = path.read_text(encoding="utf-8", errors="ignore")
    except (OSError, UnicodeError):
        return None
    # Accept "KEY=value", plain key, or first non-comment line.
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line and line.split("=", 1)[0].strip().isidentifier():
            line = line.split("=", 1)[1].strip()
        line = line.strip().strip('"').strip("'")
        if line:
            return line
    return None


@dataclass(frozen=True)
class KeyResolution:
    key: Optional[str]
    source: str


def resolve_api_key(cli_key: Optional[str],
                    cli_key_file: Optional[str]) -> KeyResolution:
    """Resolve the API key from the documented precedence chain."""
    if cli_key:
        k = cli_key.strip()
        if k:
            return KeyResolution(k, "--api-key")

    if cli_key_file:
        p = Path(cli_key_file).expanduser()
        if not p.is_file():
            raise FileNotFoundError(f"--api-key-file not found: {p}")
        k = _read_key_file(p)
        if not k:
            raise ValueError(f"--api-key-file is empty / unparsable: {p}")
        return KeyResolution(k, f"--api-key-file ({p})")

    env_key = os.environ.get(KEY_ENV_VAR, "").strip()
    if env_key:
        return KeyResolution(env_key, f"${KEY_ENV_VAR}")

    env_file = os.environ.get(KEY_FILE_ENV_VAR, "").strip()
    if env_file:
        p = Path(env_file).expanduser()
        k = _read_key_file(p) if p.is_file() else None
        if k:
            return KeyResolution(k, f"${KEY_FILE_ENV_VAR} ({p})")
        log(f"WARN: ${KEY_FILE_ENV_VAR} points to an unusable file: {p}")

    if DEFAULT_KEY_PATH.is_file():
        k = _read_key_file(DEFAULT_KEY_PATH)
        if k:
            return KeyResolution(k, f"default key file ({DEFAULT_KEY_PATH})")

    return KeyResolution(None, "unresolved")


# --------------------------------------------------------------------------- #
# Input file loading
# --------------------------------------------------------------------------- #

@dataclass
class Artefact:
    label: str
    path: Optional[Path]
    content: str
    ok: bool
    note: str = ""
    language: str = "python"


def load_artefact(label: str,
                  path_str: Optional[str],
                  max_bytes: int,
                  language: str = "python") -> Artefact:
    if not path_str:
        return Artefact(label, None, "", False,
                        "NOT PROVIDED (no path given on the command line)",
                        language)

    path = Path(path_str).expanduser()
    if not path.exists():
        return Artefact(label, path, "", False,
                        f"FILE NOT FOUND: {path}", language)
    if path.is_dir():
        return Artefact(label, path, "", False,
                        f"PATH IS A DIRECTORY, not a file: {path}", language)
    try:
        data = path.read_bytes()
    except OSError as exc:
        return Artefact(label, path, "", False,
                        f"UNREADABLE ({exc.__class__.__name__}: {exc}): {path}",
                        language)

    note = ""
    if len(data) > max_bytes:
        head = max_bytes // 2
        tail = max_bytes - head
        data = (data[:head]
                + b"\n\n... [TRUNCATED BY REVIEW HARNESS] ...\n\n"
                + data[-tail:])
        note = (f"TRUNCATED: original size {human_bytes(path.stat().st_size)} "
                f"exceeded per-file cap {human_bytes(max_bytes)}")

    text = data.decode("utf-8", errors="replace")
    # Prevent nested