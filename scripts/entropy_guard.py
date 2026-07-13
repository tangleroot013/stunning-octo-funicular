#!/usr/bin/env python3
"""Shannon-entropy scan: flag high-entropy strings that look like secrets or keys."""

import math
import re
import sys
from pathlib import Path

THRESHOLD = 4.5
MIN_LEN = 20

def entropy(s: str) -> float:
    if not s:
        return 0
    prob = [s.count(c) / len(s) for c in set(s)]
    return -sum(p * math.log2(p) for p in prob)

def scan() -> int:
    hits = 0
    for py in Path(".").rglob("*"):
        if ".git" in str(py) or py.is_dir() or py.stat().st_size > 1_000_000:
            continue
        try:
            text = py.read_text(errors="ignore")
        except Exception:
            continue
        for line in text.splitlines():
            for token in re.findall(r'["\\']([A-Za-z0-9+/=]{20,})["\\']', line):
                e = entropy(token)
                if e > THRESHOLD:
                    print(f"🚨 High entropy ({e:.2f}) in {py}: {token[:16]}...")
                    hits += 1
    if hits:
        print(f"\\n❌ {hits} high-entropy string(s) detected. May be secrets.")
        return 1
    print("✅ No high-entropy strings found.")
    return 0

if __name__ == "__main__":
    sys.exit(scan())
