#!/usr/bin/env python3
"""Prune remote tracking branches that no longer exist on origin."""

import subprocess
from pathlib import Path

def prune() -> None:
    before = subprocess.check_output(["git", "branch", "-r"], text=True).splitlines()
    subprocess.run(["git", "remote", "prune", "origin"], check=True)
    after = subprocess.check_output(["git", "branch", "-r"], text=True).splitlines()
    removed = set(before) - set(after)
    if removed:
        print(f"🗑️  Pruned {len(removed)} stale remote branch(es):")
        for b in removed:
            print(f"   {b.strip()}")
    else:
        print("✅ No stale remote branches to prune.")

if __name__ == "__main__":
    prune()
