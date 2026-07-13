#!/usr/bin/env python3
"""Per-author line ownership report for src/ using git blame."""

import subprocess
from collections import defaultdict
from pathlib import Path

def blame() -> None:
    authors = defaultdict(int)
    for py in Path("src").rglob("*.py"):
        try:
            result = subprocess.check_output(
                ["git", "blame", "--line-porcelain", str(py)],
                text=True, errors="ignore"
            )
            for line in result.splitlines():
                if line.startswith("author "):
                    authors[line[7:]] += 1
        except subprocess.CalledProcessError:
            pass
    
    total = sum(authors.values())
    print("# Code Ownership (by lines)\n")
    for author, lines in sorted(authors.items(), key=lambda x: -x[1])[:10]:
        pct = lines / total * 100 if total else 0
        bar = "█" * int(pct / 2)
        print(f"{author:20} {bar} {lines:,} lines ({pct:.1f}%)")

if __name__ == "__main__":
    blame()
