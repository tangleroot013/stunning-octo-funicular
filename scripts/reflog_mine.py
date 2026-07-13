#!/usr/bin/env python3
"""Mine git reflog for lost commits and dangling references."""

import subprocess
from datetime import datetime
from pathlib import Path

def mine() -> None:
    reflog = subprocess.check_output(["git", "reflog", "--all"], text=True).splitlines()
    print(f"# Reflog Analysis ({len(reflog)} entries)\n")
    
    orphans = []
    for line in reflog[:50]:
        parts = line.split()
        if len(parts) >= 2:
            sha = parts[0]
            action = " ".join(parts[1:])
            # Check if reachable from any branch
            result = subprocess.run(
                ["git", "branch", "--contains", sha],
                capture_output=True, text=True
            )
            if not result.stdout.strip():
                orphans.append((sha, action))
    
    if orphans:
        print("## Potentially Lost Commits")
        for sha, action in orphans[:10]:
            print(f"- `{sha[:8]}` {action}")
    else:
        print("✅ All reflog entries reachable from branches.")

if __name__ == "__main__":
    mine()
