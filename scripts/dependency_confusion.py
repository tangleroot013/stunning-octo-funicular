#!/usr/bin/env python3
"""Detect private package names that could be hijacked on public PyPI."""

import subprocess
import sys
from pathlib import Path

def audit() -> int:
    req = Path("requirements.txt")
    if not req.exists():
        print("ℹ️  No requirements.txt found.")
        return 0
    
    packages = [line.split("==")[0] for line in req.read_text().splitlines() if "==" in line]
    
    hits = 0
    for pkg in packages:
        # Check if package exists on PyPI
        import urllib.request
        try:
            urllib.request.urlopen(f"https://pypi.org/pypi/{pkg}/json", timeout=3)
            # Package exists publicly — if it's supposed to be private, that's a risk
            print(f"⚠️  {pkg}: exists on public PyPI — if private, use private index")
            hits += 1
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"✅ {pkg}: not on public PyPI (safe from confusion)")
            else:
                print(f"⚠️  {pkg}: PyPI check failed ({e.code})")
    
    if hits:
        print(f"\n⚠️  {hits} package(s) on public PyPI. Use --index-url for private packages.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
