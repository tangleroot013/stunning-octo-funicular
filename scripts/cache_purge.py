#!/usr/bin/env python3
"""Aggressively purge all Python cache artifacts, .egg-info, and build debris."""

import shutil
import sys
from pathlib import Path

TARGETS = ["__pycache__", "*.egg-info", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".coverage", "htmlcov", "build", "dist"]

def purge() -> int:
    removed = 0
    for pattern in TARGETS:
        for p in Path(".").rglob(pattern):
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
                print(f"🗑️  {p}")
                removed += 1
            elif p.is_file():
                p.unlink()
                print(f"🗑️  {p}")
                removed += 1
    print(f"✅ Purged {removed} artifact(s).")
    return 0

if __name__ == "__main__":
    sys.exit(purge())
