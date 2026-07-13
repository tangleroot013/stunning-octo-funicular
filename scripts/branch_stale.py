#!/usr/bin/env python3
"""Identify local branches with no upstream and no commits in 30 days."""

import subprocess
from datetime import datetime, timedelta
from pathlib import Path

def find() -> None:
    branches = subprocess.check_output(
        ["git", "for-each-ref", "--format=%(refname:short) %(upstream:short) %(committerdate:unix)", "refs/heads"],
        text=True
    ).splitlines()
    
    cutoff = datetime.now() - timedelta(days=30)
    stale = []
    
    for line in branches:
        parts = line.split()
        if len(parts) < 3:
            continue
        name, upstream, ts = parts[0], parts[1] if len(parts) > 1 else "", int(parts[-1])
        last_commit = datetime.fromtimestamp(ts)
        
        if (not upstream or upstream == name) and last_commit < cutoff:
            stale.append((name, (datetime.now() - last_commit).days))
    
    if stale:
        print(f"# Stale Branches ({len(stale)} found)\n")
        for name, days in sorted(stale, key=lambda x: -x[1]):
            print(f"  🗑️  {name:<30} {days} days idle")
        print(f"\nDelete: git branch -D <name>")
    else:
        print("✅ No stale branches.")

if __name__ == "__main__":
    find()
