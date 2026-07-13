#!/usr/bin/env python3
"""Interactively squash last N commits into one with a clean message."""

import subprocess
import sys
from pathlib import Path

def squash(n: int = 3) -> int:
    if n < 2:
        print("ℹ️  Nothing to squash.")
        return 0
    
    # Show commits
    log = subprocess.check_output(["git", "log", f"-{n}", "--oneline"], text=True)
    print(f"Commits to squash:\\n{log}")
    
    confirm = input(f"\\nSquash last {n} into one? [y/N]: ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        return 0
    
    # Soft reset and commit
    subprocess.run(["git", "reset", "--soft", f"HEAD~{n}"], check=True)
    msg = input("New commit message: ").strip()
    if not msg:
        msg = f"chore: squash {n} commits"
    subprocess.run(["git", "commit", "-m", msg], check=True)
    print(f"✅ Squashed {n} commits into: {msg}")
    return 0

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    sys.exit(squash(n))
