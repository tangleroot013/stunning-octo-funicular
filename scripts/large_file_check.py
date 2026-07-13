#!/usr/bin/env python3
"""Warn about tracked files exceeding 100KB (GitHub soft limit)."""

import subprocess
import sys
from pathlib import Path

THRESHOLD_KB = 100

def check() -> int:
    files = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
    offenders = []
    for f in files:
        p = Path(f)
        if p.is_file():
            kb = p.stat().st_size / 1024
            if kb > THRESHOLD_KB:
                offenders.append((f, kb))
    if offenders:
        print(f"⚠️  Files > {THRESHOLD_KB}KB:")
        for f, kb in sorted(offenders, key=lambda x: -x[1]):
            print(f"   {f}: {kb:.1f} KB")
        return 1
    print("✅ All tracked files under threshold.")
    return 0

if __name__ == "__main__":
    sys.exit(check())
