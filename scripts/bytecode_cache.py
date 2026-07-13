#!/usr/bin/env python3
"""Verify __pycache__ coverage and flag stale .pyc files older than their .py source."""

import os
import sys
from pathlib import Path

def audit() -> int:
    stale = 0
    missing = 0
    for py in Path("src").rglob("*.py"):
        cache = py.with_suffix(".pyc")
        cache_dir = py.parent / "__pycache__" / (py.stem + ".cpython-311.pyc")
        if not cache.exists() and not cache_dir.exists():
            missing += 1
            continue
        check = cache_dir if cache_dir.exists() else cache
        if check.stat().st_mtime < py.stat().st_mtime:
            print(f"⚠️  Stale bytecode: {check}")
            stale += 1
            os.remove(check)
    
    if missing:
        print(f"⚠️  {missing} file(s) missing cached bytecode. Run: python -m compileall src/")
    if stale:
        print(f"🗑️  Removed {stale} stale .pyc file(s)")
    if not missing and not stale:
        print("✅ All bytecode caches fresh and valid.")
    return 1 if (missing or stale) else 0

if __name__ == "__main__":
    sys.exit(audit())
