#!/usr/bin/env python3
"""Interactive fzf launcher for all scripts in the directory."""

import subprocess
import sys
from pathlib import Path

def menu() -> int:
    scripts = sorted(Path("scripts").glob("*.py"))
    if not scripts:
        print("ℹ️  No scripts found.")
        return 0
    names = "\n".join(s.stem.replace("_", "-") for s in scripts)
    try:
        choice = subprocess.check_output(
            ["fzf", "--prompt", "run script> ", "--preview", "cat {}"],
            input=names,
            text=True
        ).strip().replace("-", "_")
    except subprocess.CalledProcessError:
        return 0
    target = Path("scripts") / f"{choice}.py"
    if target.exists():
        print(f"▶ {target}")
        return subprocess.run([sys.executable, str(target)]).returncode
    return 1

if __name__ == "__main__":
    sys.exit(menu())
