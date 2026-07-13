#!/usr/bin/env python3
"""Summarize recent git activity: commits, authors, files changed."""

import subprocess
from collections import Counter
from pathlib import Path

def report() -> None:
    commits = subprocess.check_output(
        ["git", "log", "--since=7.days", "--pretty=%h|%an|%s"],
        text=True
    ).splitlines()
    if not commits:
        print("ℹ️  No commits in last 7 days.")
        return
    authors = Counter(c.split("|")[1] for c in commits)
    print(f"# Git Activity (last 7 days)\\n")
    print(f"**Commits:** {len(commits)}")
    print(f"**Authors:** {len(authors)}")
    print("\\n## Top Contributors")
    for author, count in authors.most_common(5):
        print(f"- {author}: {count}")
    files = subprocess.check_output(
        ["git", "log", "--since=7.days", "--name-only", "--pretty=format:"],
        text=True
    ).splitlines()
    changed = Counter(f for f in files if f)
    print("\\n## Most Changed Files")
    for f, count in changed.most_common(5):
        print(f"- {f}: {count}")

if __name__ == "__main__":
    report()
