#!/usr/bin/env python3
"""Generate CHANGELOG.md from conventional commits."""

import subprocess
from collections import defaultdict
from pathlib import Path

CATEGORIES = {
    "feat": "Features",
    "fix": "Bug Fixes",
    "chore": "Chores",
    "docs": "Documentation",
    "refactor": "Refactors",
}

def commits_since(tag: str) -> list[str]:
    cmd = ["git", "log", f"{tag}..HEAD", "--pretty=format:%s"]
    return subprocess.check_output(cmd, text=True).strip().splitlines()

def parse(commits: list[str]) -> dict[str, list[str]]:
    buckets: dict[str, list[str]] = defaultdict(list)
    for msg in commits:
        if ":" in msg:
            prefix, body = msg.split(":", 1)
            cat = CATEGORIES.get(prefix.strip(), "Other")
            buckets[cat].append(f"- {body.strip()}")
    return buckets

def write(tag: str) -> None:
    lines = [f"## Unreleased changes since {tag}\n"]
    for cat in CATEGORIES.values():
        if entries := parse(commits_since(tag)).get(cat):
            lines.append(f"### {cat}\n")
            lines.extend(entries)
            lines.append("")
    Path("CHANGELOG.md").write_text("\n".join(lines))
    print("✅ CHANGELOG.md updated.")

if __name__ == "__main__":
    write("v0.2.2")
