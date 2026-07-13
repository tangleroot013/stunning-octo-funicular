#!/usr/bin/env python3
"""Verify virtualenv is active and Python version matches pyproject.toml."""

import sys
from pathlib import Path

def check() -> int:
    in_venv = hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
    if not in_venv:
        print("❌ No virtualenv active. Run: source .venv/bin/activate")
        return 1
    pyproject = Path("pyproject.toml")
    if pyproject.exists():
        text = pyproject.read_text()
        import re
        m = re.search(r'target-version = \["py(\d)(\d+)"\]', text)
        if m:
            expected = f"{m.group(1)}.{m.group(2)}"
            actual = f"{sys.version_info.major}.{sys.version_info.minor}"
            if actual != expected:
                print(f"❌ Python {actual} != required {expected}")
                return 1
    print(f"✅ venv active, Python {sys.version_info.major}.{sys.version_info.minor}")
    return 0

if __name__ == "__main__":
    sys.exit(check())
