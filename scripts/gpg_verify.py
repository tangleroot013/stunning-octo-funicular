#!/usr/bin/env python3
"""Verify GPG signature coverage on the last N commits."""

import subprocess
import sys

def verify(count: int = 20) -> int:
    log = subprocess.check_output(
        ["git", "log", f"-{count}", "--pretty=%H|%G?|%s"],
        text=True
    ).splitlines()
    signed = 0
    for line in log:
        sha, status, msg = line.split("|", 2)
        if status in ("G", "U"):
            signed += 1
        elif status == "B":
            print(f"🚨 BAD signature on {sha[:8]}: {msg}")
            return 1
        elif status == "N":
            print(f"⚠️  Unsigned: {sha[:8]} {msg}")
    pct = signed / len(log) * 100 if log else 0
    print(f"✅ GPG coverage: {signed}/{len(log)} ({pct:.0f}%)")
    return 0

if __name__ == "__main__":
    sys.exit(verify())
