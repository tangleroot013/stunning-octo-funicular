#!/usr/bin/env python3
"""List local branches that are behind or ahead of their remote tracking ref."""

import subprocess
from pathlib import Path

def check() -> None:
    subprocess.run(["git", "fetch", "--prune"], capture_output=True)
    branches = subprocess.check_output(
        ["git", "for-each-ref", "--format=%(refname:short) %(upstream:short)", "refs/heads"],
        text=True
    ).splitlines()
    for line in branches:
        local, remote = line.split()
        if not remote or remote == local:
            continue
        try:
            ahead_behind = subprocess.check_output(
                ["git", "rev-list", "--left-right", "--count", f"{remote}...{local}"],
                text=True
            ).strip()
            behind, ahead = map(int, ahead_behind.split())
            if behind or ahead:
                print(f"⚠️  {local}: {ahead} ahead, {behind} behind {remote}")
        except subprocess.CalledProcessError:
            print(f"❌ {local}: no remote tracking branch {remote}")

if __name__ == "__main__":
    check()
