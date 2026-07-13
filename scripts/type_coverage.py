#!/usr/bin/env python3
"""Rough type-coverage estimate via mypy --linecount and grep."""

import subprocess
from pathlib import Path

def estimate() -> None:
    total = 0
    typed = 0
    for py in Path("src").rglob("*.py"):
        lines = py.read_text().splitlines()
        total += len(lines)
        typed += sum(1 for l in lines if ":" in l and ("def " in l or "-> " in l))
    pct = (typed / total * 100) if total else 0
    print(f"📊 Type coverage estimate: {pct:.1f}% ({typed}/{total} lines)")

if __name__ == "__main__":
    estimate()
