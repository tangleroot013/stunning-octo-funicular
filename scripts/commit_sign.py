#!/usr/bin/env python3
"""Verify all commits since last tag are GPG-signed."""

import subprocess
import sys
from pathlib import Path

def verify() -> int:
    try:
        last_tag = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"], text=True).strip()
    except subprocess.CalledProcessError:
        last_tag = "HEAD~20"
    
    log = subprocess.check_output(
        ["git", "log", f"{last_tag}..HEAD", "--pretty=%H|%G?|%s"],
        text=True
    ).splitlines()
    
    unsigned = []
    for line in log:
        sha, status, msg = line.split("|", 2)
        if status not in ("G", "U"):
            unsigned.append((sha[:8], msg[:50]))
    
    if unsigned:
        print(f"❌ {len(unsigned)} unsigned commit(s) since {last_tag}:")
        for sha, msg in unsigned:
            print(f"   {sha} {msg}")
        return 1
    print(f"✅ All {len(log)} commits since {last_tag} are signed.")
    return 0

if __name__ == "__main__":
    sys.exit(verify())
