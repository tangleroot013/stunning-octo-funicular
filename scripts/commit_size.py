#!/usr/bin/env python3
"""Flag commits exceeding a line-change threshold (default 500 lines)."""

import subprocess
import sys
from pathlib import Path

THRESHOLD = 500

def check() -> int:
    log = subprocess.check_output(
        ["git", "log", "--since=30.days", "--pretty=%H|%s", "--shortstat"],
        text=True
    )
    
    chunks = log.split("\n\n")
    offenders = []
    for chunk in chunks:
        lines = chunk.strip().splitlines()
        if len(lines) < 2:
            continue
        header = lines[0]
        sha = header.split("|")[0]
        msg = header.split("|")[1] if "|" in header else ""
        stats = lines[-1]
        if "changed" in stats:
            parts = stats.split(",")
            total = sum(int(p.split()[0]) for p in parts if p.strip().split()[0].isdigit())
            if total > THRESHOLD:
                offenders.append((sha[:8], total, msg[:50]))
    
    if offenders:
        print(f"⚠️  {len(offenders)} commit(s) > {THRESHOLD} lines:")
        for sha, total, msg in offenders:
            print(f"   {sha} {total:4} lines: {msg}")
        return 1
    print(f"✅ All commits under {THRESHOLD} lines.")
    return 0

if __name__ == "__main__":
    sys.exit(check())
