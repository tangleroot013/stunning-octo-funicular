#!/usr/bin/env python3
"""Compare .env against .env.example and report drift."""

import sys
from pathlib import Path

def parse_env(path: Path) -> dict[str, str]:
    vals = {}
    if not path.exists():
        return vals
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            vals[k.strip()] = v.strip()
    return vals

def diff() -> int:
    a = parse_env(Path(".env"))
    b = parse_env(Path(".env.example"))
    missing = set(b) - set(a)
    extra = set(a) - set(b)
    changed = {k for k in a if k in b and a[k] != b[k]}
    if missing:
        print(f"❌ Missing in .env: {missing}")
    if extra:
        print(f"⚠️  Extra in .env: {extra}")
    if changed:
        print(f"⚠️  Values differ: {changed}")
    if not any((missing, extra, changed)):
        print("✅ .env and .env.example are in sync.")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(diff())
