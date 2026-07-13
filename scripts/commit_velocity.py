#!/usr/bin/env python3
"""Show commit velocity histogram for the last 30 days."""

import subprocess
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

def velocity() -> None:
    log = subprocess.check_output(
        ["git", "log", "--since=30.days", "--pretty=%ad"],
        text=True
    ).splitlines()
    if not log:
        print("ℹ️  No commits in last 30 days.")
        return
    counts = Counter(datetime.strptime(d, "%a %b %d %H:%M:%S %Y %z").strftime("%Y-%m-%d") for d in log)
    print("# Commit Velocity (last 30 days)\\n")
    for i in range(30, -1, -1):
        d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        bar = "█" * counts.get(d, 0)
        print(f"{d} {bar or '·'}")
    print(f"\\nTotal: {len(log)} commits | Avg: {len(log)/30:.1f}/day")

if __name__ == "__main__":
    velocity()
