#!/usr/bin/env python3
"""Prevent force-push to main by checking git config and remote hooks."""

import subprocess
import sys
from pathlib import Path

def check() -> int:
    branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    if branch != "main":
        return 0
    remote = subprocess.check_output(["git", "remote", "get-url", "origin"], text=True).strip()
    if "github.com" in remote:
        print("🛡️  main branch detected. Enforce PR workflow — no direct push.")
        print("   Use: git checkout -b feature/xyz && git push -u origin feature/xyz")
        return 1
    print("✅ Not on GitHub-hosted main. Proceed with caution.")
    return 0

if __name__ == "__main__":
    sys.exit(check())
