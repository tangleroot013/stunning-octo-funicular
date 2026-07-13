#!/usr/bin/env python3
"""Check for missing .pyi stub files for public modules."""

import sys
from pathlib import Path

def check() -> int:
    missing = []
    for py in Path("src").rglob("*.py"):
        stub = py.with_suffix(".pyi")
        if not stub.exists() and not py.name.startswith("_"):
            missing.append(str(py.relative_to("src")))
    if missing:
        print(f"⚠️  {len(missing)} modules missing .pyi stubs:")
        for m in missing[:5]:
            print(f"   {m}")
        return 1
    print("✅ All public modules have stub files.")
    return 0

if __name__ == "__main__":
    sys.exit(check())
