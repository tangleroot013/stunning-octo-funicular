#!/usr/bin/env python3
"""Detect non-ASCII characters or BOM markers in Python source files."""

import sys
from pathlib import Path

def scan() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        raw = py.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            print(f"🚨 BOM detected: {py}")
            hits += 1
        try:
            raw.decode("ascii")
        except UnicodeDecodeError:
            for i, line in enumerate(raw.decode("utf-8").splitlines(), 1):
                try:
                    line.encode("ascii")
                except UnicodeEncodeError:
                    print(f"⚠️  Non-ASCII in {py}:{i}")
                    hits += 1
                    break
    if hits:
        return 1
    print("✅ All source files are ASCII-clean.")
    return 0

if __name__ == "__main__":
    sys.exit(scan())
