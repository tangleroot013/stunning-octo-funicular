#!/usr/bin/env python3
"""Verify mypy strictness in pyproject.toml matches team policy."""

import re
import sys
from pathlib import Path

POLICY = {"strict": True, "disallow_untyped_defs": True, "disallow_untyped_calls": True}

def check() -> int:
    text = Path("pyproject.toml").read_text()
    mypy = text.split("[tool.mypy]")[1].split("[")[0] if "[tool.mypy]" in text else ""
    missing = [k for k, v in POLICY.items() if v and f"{k} = true" not in mypy]
    if missing:
        print(f"❌ mypy missing strict flags: {missing}")
        return 1
    print("✅ mypy strictness policy enforced.")
    return 0

if __name__ == "__main__":
    sys.exit(check())
