#!/usr/bin/env python3
"""Calculate average time from PR open to merge for merged PRs."""

import subprocess
import json
from datetime import datetime
from pathlib import Path

def window() -> None:
    result = subprocess.run(
        ["gh", "pr", "list", "--state", "merged", "--json", "createdAt,mergedAt", "-L", "100"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"❌ gh CLI error: {result.stderr}")
        return
    
    prs = json.loads(result.stdout)
    durations = []
    for pr in prs:
        created = datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00"))
        merged = datetime.fromisoformat(pr["mergedAt"].replace("Z", "+00:00"))
        durations.append((merged - created).total_seconds() / 3600)
    
    if durations:
        avg = sum(durations) / len(durations)
        print(f"# Merge Window Analysis ({len(durations)} PRs)\n")
        print(f"Average: {avg:.1f} hours")
        print(f"Median:  {sorted(durations)[len(durations)//2]:.1f} hours")
        print(f"Fastest: {min(durations):.1f} hours")
        print(f"Slowest: {max(durations):.1f} hours")
    else:
        print("ℹ️  No merged PRs found.")

if __name__ == "__main__":
    window()
