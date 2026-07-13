#!/usr/bin/env python3
"""Generate Co-authored-by trailers from recent pair/mob programming sessions."""

import subprocess
from pathlib import Path

def generate() -> None:
    # Get unique authors from last 5 commits
    authors = set(subprocess.check_output(
        ["git", "log", "-5", "--pretty=%an <%ae>"],
        text=True
    ).splitlines())
    
    me = subprocess.check_output(["git", "config", "user.email"], text=True).strip()
    coauthors = [a for a in authors if me not in a]
    
    if not coauthors:
        print("ℹ️  No co-authors detected.")
        return
    
    print("# Co-authored-by trailers:\n")
    for author in coauthors:
        print(f"Co-authored-by: {author}")
    print(f"\nAppend to commit: git commit --amend --no-edit -m \"$(git log -1 --pretty=%B)\"")

if __name__ == "__main__":
    generate()
