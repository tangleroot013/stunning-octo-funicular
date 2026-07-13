#!/usr/bin/env python3
"""Find oldest lines in critical files (hatch.py, ship.py) via git blame."""

import subprocess
from pathlib import Path

TARGETS = ["hatch.py", "ship.py", "settings.json"]

def analyze() -> None:
    for f in TARGETS:
        if not Path(f).exists():
            continue
        result = subprocess.check_output(
            ["git", "blame", "--date=short", "-L", "1,10", f],
            text=True
        )
        oldest = min(line.split("(")[1].split()[1] for line in result.splitlines() if "(" in line)
        print(f"📅 {f}: oldest line dated {oldest}")

if __name__ == "__main__":
    analyze()
