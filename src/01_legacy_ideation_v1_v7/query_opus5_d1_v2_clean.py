#!/usr/bin/env python3
"""
query_opus5_d1_v2.py  --  Brutal Multipoint Quality Inspection query utility.

Purpose
-------
Assemble a review prompt out of three local source artifacts (data freezer,
signal generator, causality test) and send it to an OpenRouter chat-completions
model, then persist the reasoning + response to a Markdown file.

Hard rules enforced by this utility
-----------------------------------
1.  NO hard-coded secrets.  The API key is resolved, in order, from:
        --api-key  ->  $OPENROUTER_API_KEY  ->  $OPENROUTER_KEY
        ->  ~/.openrouter_key  ->  ./.openrouter_key
2.  Missing key is NOT fatal.  The script degrades gracefully to an offline
    "dry-run": the fully rendered prompt is written to disk, a clear notice is
    printed, and the process exits 0.  Nothing crashes.
3.  Missing / unreadable source files are NOT fatal.  A clearly-marked
    placeholder block is substituted so the prompt remains well-formed.
4.  All network I/O is bounded (timeout) and retried with exponential backoff
    + jitter on transient failures (429 / 5xx / connection errors).
5.  Response parsing is fully defensive (empty choices, list-shaped content,
    missing keys, non-JSON bodies).
6.  Every code fence is built from a `chr(96) * 3` constant, so there is no
    possibility of an unterminated string literal or fence collision with the
    embedded source code.
7.  Output directories are created on demand; files are written UTF-8 with
    an atomic replace.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

BACKTICK = chr(96)                 # '`'
FENCE = BACKTICK * 3               # '