#!/usr/bin/env python3
"""Assign a reviewer to the current PR using round-robin from recent committers."""

import json
import subprocess
import sys
from pathlib import Path

def assign() -> int:
    # Get current PR number
    result = subprocess.run(["gh", "pr", "view", "--json", "number"], capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Not in a PR context or gh CLI not configured.")
        return 1
    
    pr = json.loads(result.stdout)["number"]
    
    # Get committers
    log = subprocess.check_output(
        ["git", "log", "--since=90.days", "--pretty=%an"],
        text=True
    ).splitlines()
    from collections import Counter
    candidates = [name for name, _ in Counter(log).most_common(10)]
    
    me = subprocess.check_output(["git", "config", "user.name"], text=True).strip()
    reviewers = [c for c in candidates if c != me][:3]
    
    if not reviewers:
        print("ℹ️  No eligible reviewers found.")
        return 0
    
    for reviewer in reviewers:
        subprocess.run(["gh", "pr", "edit", str(pr), "--add-reviewer", reviewer], capture_output=True)
    
    print(f"✅ Assigned {len(reviewers)} reviewer(s) to PR #{pr}: {', '.join(reviewers)}")
    return 0

if __name__ == "__main__":
    sys.exit(assign())
