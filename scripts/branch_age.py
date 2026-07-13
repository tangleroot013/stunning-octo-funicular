#!/usr/bin/env python3
"""Warn about local branches older than 14 days without commits."""

import subprocess
from datetime import datetime, timedelta
from pathlib import Path

THRESHOLD_DAYS = 14

def check() -> None:
    branches = subprocess.check_output(
        ["git", "for-each-ref", "--format=%(refname:short) %(committerdate:short)", "refs/heads"],
        text=True
    ).splitlines()
    stale = []
    for line in branches:
        name, date_str = line.rsplit(" ", 1)
        date = datetime.strptime(date_str, "%Y-%m-%d")
        if datetime.now() - date > timedelta(days=THRESHOLD_DAYS):
            stale.append(f"- {name} (last commit {date_str})")
    if stale:
        print(f"⚠️  Stale branches (> {THRESHOLD_DAYS} days):")
        print("\n".join(stale))
    else:
        print("✅ All branches fresh.")

if __name__ == "__main__":
    check()
