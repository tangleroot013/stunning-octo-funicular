#!/usr/bin/env python3
"""Detect duplicate or conflicting package entries in requirements.txt."""

import re
import sys
from pathlib import Path

def audit() -> int:
    req = Path("requirements.txt")
    if not req.exists():
        print("ℹ️  No requirements.txt found.")
        return 0
    packages = {}
    for line in req.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"([a-zA-Z0-9_-]+)", line)
        if m:
            name = m.group(1).lower()
            packages.setdefault(name, []).append(line)
    dups = {k: v for k, v in packages.items() if len(v) > 1}
    if dups:
        print(f"❌ Duplicate/conflicting entries:")
        for name, entries in dups.items():
            for e in entries:
                print(f"   {e}")
        return 1
    print(f"✅ {len(packages)} unique packages, no conflicts.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
