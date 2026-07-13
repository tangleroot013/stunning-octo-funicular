#!/usr/bin/env python3
"""Verify docs/ directory exists and contains expected index files."""

import sys
from pathlib import Path

REQUIRED = ("index.md", "README.md", "api.md")

def check() -> int:
    docs = Path("docs")
    if not docs.exists():
        print("❌ docs/ directory missing.")
        return 1
    missing = [f for f in REQUIRED if not (docs / f).exists()]
    if missing:
        print(f"⚠️  docs/ missing: {missing}")
        return 1
    print(f"✅ docs/ present with {len(REQUIRED)} expected files.")
    return 0

if __name__ == "__main__":
    sys.exit(check())
