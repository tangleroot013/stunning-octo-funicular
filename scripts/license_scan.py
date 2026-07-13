#!/usr/bin/env python3
"""Verify all .py files in src/ start with the project license header."""

import sys
from pathlib import Path

HEADER = "# stunning-octo-funicular"

def scan() -> int:
    missing = []
    for py in Path("src").rglob("*.py"):
        if not py.read_text().startswith(HEADER):
            missing.append(str(py))
    if missing:
        print(f"❌ {len(missing)} files missing license header:")
        for f in missing[:5]:
            print(f"   {f}")
        return 1
    print("✅ All source files have license header.")
    return 0

if __name__ == "__main__":
    sys.exit(scan())
