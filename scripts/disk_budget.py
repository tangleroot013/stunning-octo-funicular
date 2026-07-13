#!/usr/bin/env python3
"""Warn if project directory exceeds a size budget (default 100MB)."""

import sys
from pathlib import Path

BUDGET_MB = 100

def check() -> int:
    total = sum(f.stat().st_size for f in Path(".").rglob("*") if f.is_file() and ".git" not in str(f))
    mb = total / (1024 * 1024)
    print(f"📊 Project size: {mb:.1f} MB (budget: {BUDGET_MB} MB)")
    if mb > BUDGET_MB:
        print("❌ Budget exceeded. Largest directories:")
        dirs = {}
        for d in Path(".").rglob("*"):
            if d.is_dir() and ".git" not in str(d):
                s = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
                dirs[str(d)] = s / (1024 * 1024)
        for d, s in sorted(dirs.items(), key=lambda x: -x[1])[:5]:
            print(f"   {d}: {s:.1f} MB")
        return 1
    print("✅ Within budget.")
    return 0

if __name__ == "__main__":
    sys.exit(check())
