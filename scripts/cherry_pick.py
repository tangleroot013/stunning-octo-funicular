#!/usr/bin/env python3
"""Interactive cherry-pick: show commits on branch not on main, pick by number."""

import subprocess
import sys
from pathlib import Path

def pick() -> int:
    branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    log = subprocess.check_output(
        ["git", "log", "main..HEAD", "--oneline"],
        text=True
    ).splitlines()
    
    if not log:
        print("ℹ️  No commits ahead of main.")
        return 0
    
    print(f"# Commits on {branch} not in main:\n")
    for i, line in enumerate(log, 1):
        print(f"  {i}. {line}")
    
    choice = input("\nCherry-pick range (e.g., 1-3 or 2): ").strip()
    if "-" in choice:
        start, end = map(int, choice.split("-"))
        picks = log[start-1:end]
    else:
        picks = [log[int(choice)-1]]
    
    for commit in picks:
        sha = commit.split()[0]
        result = subprocess.run(["git", "cherry-pick", sha])
        if result.returncode != 0:
            print(f"❌ Cherry-pick failed at {sha}")
            return 1
    
    print(f"✅ Cherry-picked {len(picks)} commit(s).")
    return 0

if __name__ == "__main__":
    sys.exit(pick())
