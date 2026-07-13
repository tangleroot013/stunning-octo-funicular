#!/usr/bin/env python3
"""Heatmap of file change frequency from git log --name-only."""

import subprocess
from collections import Counter
from pathlib import Path

def heatmap() -> None:
    log = subprocess.check_output(
        ["git", "log", "--since=90.days", "--name-only", "--pretty=format:"],
        text=True
    )
    counts = Counter(f for f in log.splitlines() if f and not f.startswith(" "))
    
    print("# Change Frequency Heatmap (last 90 days)\n")
    print("| File | Changes | Heat |")
    print("|------|---------|------|")
    for f, count in counts.most_common(20):
        bar = "█" * min(count, 20)
        print(f"| {f[:40]:40} | {count:7} | {bar} |")

if __name__ == "__main__":
    heatmap()
