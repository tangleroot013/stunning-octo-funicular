#!/usr/bin/env python3
"""Find the oldest lines of code still present in src/ (survivor analysis)."""

import subprocess
from collections import defaultdict
from pathlib import Path

def age() -> None:
    survivors = defaultdict(int)
    for py in Path("src").rglob("*.py"):
        try:
            blame = subprocess.check_output(
                ["git", "blame", "--date=short", "-l", str(py)],
                text=True, errors="ignore"
            )
            for line in blame.splitlines():
                parts = line.split()
                if len(parts) >= 3:
                    date = parts[1]
                    survivors[date] += 1
        except subprocess.CalledProcessError:
            pass
    
    if not survivors:
        print("ℹ️  No blame data available.")
        return
    
    oldest = min(survivors.keys())
    print(f"# Code Survivor Analysis\n")
    print(f"Oldest surviving line: {oldest}")
    print(f"Lines from {oldest}: {survivors[oldest]}")
    print(f"\n## Lines by year")
    by_year = defaultdict(int)
    for d, count in survivors.items():
        by_year[d[:4]] += count
    for year in sorted(by_year):
        bar = "█" * (by_year[year] // max(by_year.values()) * 30 + 1)
        print(f"  {year}: {bar} {by_year[year]}")

if __name__ == "__main__":
    age()
