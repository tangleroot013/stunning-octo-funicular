#!/usr/bin/env python3
"""Ensure no lock files are tracked that should be gitignored."""

import subprocess
from pathlib import Path

LOCK_PATTERNS = ("*.lock", "package-lock.json", "yarn.lock", "Pipfile.lock")

def check() -> int:
    tracked = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
    bad = [f for f in tracked if any(Path(f).match(p) for p in LOCK_PATTERNS)]
    if bad:
        print("❌ Lock files should not be tracked:")
        for f in bad:
            print(f"   {f}")
        return 1
    print("✅ No lock files in git index.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(check())
