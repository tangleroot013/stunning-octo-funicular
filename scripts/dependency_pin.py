#!/usr/bin/env python3
"""Audit requirements.txt for unpinned or loosely pinned dependencies."""

import re
import sys
from pathlib import Path

def audit() -> int:
    req = Path("requirements.txt")
    if not req.exists():
        print("ℹ️  No requirements.txt found.")
        return 0
    
    hits = 0
    for line in req.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        # Check for unpinned
        if re.match(r"^[a-zA-Z0-9_-]+$", line):
            print(f"❌ Unpinned: {line}")
            hits += 1
            continue
        
        # Check for loose pinning (no ==)
        if "==" not in line and ">=" not in line and "~=" not in line:
            print(f"⚠️  Loosely pinned: {line}")
            hits += 1
            continue
        
        # Check for hash
        if "--hash" not in line:
            print(f"⚠️  No hash: {line}")
    
    if hits:
        print(f"\n❌ {hits} dependency(ies) not strictly pinned.")
        return 1
    print("✅ All dependencies pinned.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
