#!/usr/bin/env python3
"""Autonomous rebase: fetch, stash, rebase, unstash, and handle conflicts."""

import subprocess
import sys
from pathlib import Path

def rebase() -> int:
    branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    
    print(f"🔄 Rebasing {branch} onto origin/main...")
    
    # Stash if dirty
    dirty = subprocess.run(["git", "diff", "--quiet"], capture_output=True).returncode != 0
    if dirty:
        subprocess.run(["git", "stash", "push", "-m", "auto_rebase"], check=True)
        print("   📦 Stashed changes")
    
    # Fetch and rebase
    subprocess.run(["git", "fetch", "origin"], check=True, capture_output=True)
    result = subprocess.run(["git", "rebase", "origin/main"], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"   ❌ Conflict detected!")
        # Check if it's a trivial conflict
        conflicts = subprocess.check_output(["git", "diff", "--name-only", "--diff-filter=U"], text=True).splitlines()
        print(f"   Conflicted files: {conflicts}")
        print(f"   Resolve manually, then: git rebase --continue")
        return 1
    
    # Unstash
    if dirty:
        subprocess.run(["git", "stash", "pop"], capture_output=True)
        print("   📦 Restored stash")
    
    print(f"   ✅ Rebased {branch} onto origin/main")
    return 0

if __name__ == "__main__":
    sys.exit(rebase())
