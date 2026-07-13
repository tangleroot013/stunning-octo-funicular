#!/usr/bin/env python3
"""Lint all .sh files in repo with shellcheck if installed."""

import subprocess
import sys
from pathlib import Path

def check() -> int:
    if subprocess.run(["which", "shellcheck"], capture_output=True).returncode != 0:
        print("⚠️  shellcheck not installed. Skipping.")
        return 0
    scripts = list(Path(".").rglob("*.sh"))
    if not scripts:
        print("ℹ️  No shell scripts found.")
        return 0
    result = subprocess.run(["shellcheck"] + [str(s) for s in scripts])
    return result.returncode

if __name__ == "__main__":
    sys.exit(check())
