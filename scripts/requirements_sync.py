#!/usr/bin/env python3
"""Sync requirements.txt with pyproject.toml dependencies if present."""

import re
from pathlib import Path

def sync() -> None:
    pyproject = Path("pyproject.toml")
    req = Path("requirements.txt")
    if not pyproject.exists() or not req.exists():
        print("ℹ️  pyproject.toml or requirements.txt missing.")
        return
    text = pyproject.read_text()
    deps = re.findall(r'^dependencies = \\[([^\\]]+)\\]', text, re.MULTILINE | re.DOTALL)
    if not deps:
        print("ℹ️  No dependencies section in pyproject.toml.")
        return
    extracted = re.findall(r'"([^"]+)"', deps[0])
    req.write_text("\\n".join(extracted) + "\\n")
    print(f"✅ requirements.txt synced ({len(extracted)} deps).")

if __name__ == "__main__":
    sync()
