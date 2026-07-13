#!/usr/bin/env python3
"""Pick a random reviewer from recent committers, excluding the current author."""

import random
import subprocess
from pathlib import Path

def pick() -> None:
    log = subprocess.check_output(
        ["git", "log", "--since=30.days", "--pretty=%an"],
        text=True
    ).splitlines()
    me = subprocess.check_output(["git", "config", "user.name"], text=True).strip()
    candidates = list(set(log) - {me})
    if not candidates:
        print("ℹ️  No other committers found.")
        return
    reviewer = random.choice(candidates)
    print(f"🎲 Reviewer: {reviewer}")
    print(f"   Suggested command: git request-pull main origin {reviewer}")

if __name__ == "__main__":
    pick()
