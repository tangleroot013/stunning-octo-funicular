#!/usr/bin/env python3
"""Diff settings.json against a committed baseline (settings.json.baseline)."""

import json
import sys
from pathlib import Path

def diff() -> int:
    baseline = Path("settings.json.baseline")
    current = Path("settings.json")
    if not baseline.exists():
        print("ℹ️  No baseline found. Creating one.")
        import shutil
        shutil.copy(current, baseline)
        return 0
    a = json.loads(baseline.read_text())
    b = json.loads(current.read_text())
    if a != b:
        print("⚠️  settings.json differs from baseline.")
        for key in set(a) | set(b):
            if a.get(key) != b.get(key):
                print(f"   ~ {key}: changed")
        return 1
    print("✅ settings.json matches baseline.")
    return 0

if __name__ == "__main__":
    sys.exit(diff())
