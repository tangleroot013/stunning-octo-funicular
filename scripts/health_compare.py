#!/usr/bin/env python3
"""Compare current health score against last commit's score from git notes."""

import subprocess
import sys
from pathlib import Path

def compare() -> int:
    current_file = Path(".health_score")
    if not current_file.exists():
        print("ℹ️  No current health score.")
        return 0
    
    current = int(current_file.read_text().strip())
    
    try:
        last = subprocess.check_output(
            ["git", "notes", "--ref=health", "show", "HEAD~1"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        last_score = int(last)
        delta = current - last_score
        arrow = "↑" if delta > 0 else "↓" if delta < 0 else "→"
        print(f"Health: {last_score} → {current} ({arrow}{abs(delta)})")
        if delta < -10:
            print("🚨 Significant regression detected!")
            return 1
    except subprocess.CalledProcessError:
        print(f"Health: {current} (no baseline)")
    
    # Store current
    subprocess.run(["git", "notes", "--ref=health", "add", "-f", "-m", str(current), "HEAD"], capture_output=True)
    print("✅ Baseline updated.")
    return 0

if __name__ == "__main__":
    sys.exit(compare())
