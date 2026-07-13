#!/usr/bin/env python3
"""Scan for unresolved merge conflict markers before commit."""

import re
import subprocess
import sys
from pathlib import Path

MARKERS = re.compile(r"^(<{7}|={7}|>{7})")

def scan() -> int:
    files = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True).splitlines()
    hits = 0
    for f in files:
        path = Path(f)
        if not path.is_file():
            continue
        for i, line in enumerate(path.read_text(errors="ignore").splitlines(), 1):
            if MARKERS.match(line):
                print(f"🚨 Conflict marker in {f}:{i}: {line.strip()}")
                hits += 1
    if hits:
        print(f"\n❌ Found {hits} unresolved conflict(s). Abort.")
        return 1
    print("✅ No conflict markers detected.")
    return 0

if __name__ == "__main__":
    sys.exit(scan())
