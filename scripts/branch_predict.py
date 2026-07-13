#!/usr/bin/env python3
"""Predict merge conflicts by checking if current branch touches same files as main."""

import subprocess
from pathlib import Path

def predict() -> None:
    branch_files = set(subprocess.check_output(
        ["git", "diff", "main...HEAD", "--name-only"],
        text=True
    ).splitlines())
    
    main_files = set(subprocess.check_output(
        ["git", "diff", "HEAD...main", "--name-only"],
        text=True
    ).splitlines())
    
    overlap = branch_files & main_files
    risk = len(overlap) / max(len(branch_files), 1) * 100
    
    print(f"# Merge Conflict Prediction\n")
    print(f"Branch files:  {len(branch_files)}")
    print(f"Main changed:  {len(main_files)}")
    print(f"Overlap:       {len(overlap)} ({risk:.0f}% risk)")
    
    if overlap:
        print(f"\n## Overlapping Files")
        for f in sorted(overlap)[:15]:
            print(f"  ⚠️  {f}")
    if risk > 50:
        print(f"\n🔴 HIGH conflict risk. Rebase recommended.")
    elif risk > 20:
        print(f"\n🟡 MEDIUM risk. Review carefully.")
    else:
        print(f"\n🟢 LOW risk. Safe to merge.")

if __name__ == "__main__":
    predict()
