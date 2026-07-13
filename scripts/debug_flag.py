#!/usr/bin/env python3
"""Detect debug=True, DEBUG=1, or Flask/FastAPI debug mode in production-facing code."""

import ast
import re
import sys
from pathlib import Path

DEBUG_PATTERNS = [
    re.compile(r"debug\s*=\s*True", re.IGNORECASE),
    re.compile(r"DEBUG\s*=\s*(1|True|true)", re.IGNORECASE),
    re.compile(r"reload\s*=\s*True", re.IGNORECASE),
]

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        text = py.read_text()
        for i, line in enumerate(text.splitlines(), 1):
            for pat in DEBUG_PATTERNS:
                if pat.search(line) and not line.strip().startswith("#"):
                    print(f"🚨 {py}:{i} debug enabled: {line.strip()[:60]}")
                    print(f"   Ensure this is gated by environment, never default True")
                    hits += 1
    if hits:
        print(f"\n❌ {hits} debug flag(s) found. Gate behind ENV != 'production'.")
        return 1
    print("✅ No hardcoded debug flags.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
