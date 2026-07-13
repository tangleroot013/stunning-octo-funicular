#!/usr/bin/env python3
"""Ensure MANIFEST.in or package data includes all non-Python files needed by the package."""

import sys
from pathlib import Path

REQUIRED_NON_PY = {".json", ".yaml", ".yml", ".toml", ".txt", ".md"}

def check() -> int:
    src_files = list(Path("src").rglob("*"))
    non_py = [f for f in src_files if f.suffix in REQUIRED_NON_PY and not f.name.startswith(".")]
    
    manifest = Path("MANIFEST.in")
    if not manifest.exists():
        print("⚠️  No MANIFEST.in found. Non-Python files may be excluded from sdist:")
        for f in non_py[:10]:
            print(f"   {f.relative_to('src')}")
        return 1
    
    manifest_text = manifest.read_text()
    missing = [f for f in non_py if str(f.relative_to("src")) not in manifest_text]
    if missing:
        print(f"⚠️  {len(missing)} file(s) may be missing from MANIFEST.in:")
        for f in missing[:10]:
            print(f"   {f.relative_to('src')}")
        return 1
    print("✅ MANIFEST.in covers non-Python package files.")
    return 0

if __name__ == "__main__":
    sys.exit(check())
