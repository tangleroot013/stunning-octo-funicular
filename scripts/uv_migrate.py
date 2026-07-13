#!/usr/bin/env python3
"""Audit readiness for uv migration: check for pip-specific patterns."""

import re
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("scripts").rglob("*.py"):
        text = py.read_text()
        if "pip install" in text and "uv pip" not in text:
            print(f"⚠️  {py}: uses pip install (consider 'uv pip install')")
            hits += 1
        if "requirements.txt" in text and "pyproject.toml" not in text:
            print(f"⚠️  {py}: references requirements.txt (uv prefers pyproject.toml)")
            hits += 1
    
    # Check for setup.py or setup.cfg
    for legacy in ("setup.py", "setup.cfg"):
        if Path(legacy).exists():
            print(f"⚠️  {legacy} found (uv prefers pyproject.toml)")
            hits += 1
    
    if Path("pyproject.toml").exists():
        text = Path("pyproject.toml").read_text()
        if "build-system" in text and "setuptools" in text:
            print("⚠️  pyproject.toml uses setuptools (uv supports, but hatchling is faster)")
            hits += 1
    
    if hits:
        print(f"\\n❌ {hits} item(s) to address before uv migration.")
        return 1
    print("✅ Repository looks uv-ready.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
