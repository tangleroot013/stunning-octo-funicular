#!/usr/bin/env python3
"""Block force pushes to protected branches via pre-push hook logic."""

import subprocess
import sys
from pathlib import Path

PROTECTED = {"main", "master", "release/*"}

def is_protected(name: str) -> bool:
    return any(name == p or name.startswith(p.rstrip("*")) for p in PROTECTED)

def guard() -> int:
    # Read push refs from stdin (called as hook)
    for line in sys.stdin:
        local_sha, remote_sha, ref_name = line.strip().split()
        branch = ref_name.replace("refs/heads/", "")
        
        if is_protected(branch):
            # Check if it's a force push
            result = subprocess.run(
                ["git", "merge-base", "--is-ancestor", local_sha, remote_sha],
                capture_output=True
            )
            if result.returncode != 0:
                print(f"🚨 FORCE PUSH BLOCKED to protected branch: {branch}")
                print(f"   Use: git push --force-with-lease origin {branch}")
                return 1
    
    print("✅ Push allowed.")
    return 0

if __name__ == "__main__":
    sys.exit(guard())
