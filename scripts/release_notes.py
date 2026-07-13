#!/usr/bin/env python3
"""Generate release notes from conventional commits since last tag."""

import subprocess
from collections import defaultdict
from pathlib import Path

CATEGORIES = {
    "feat": "✨ Features",
    "fix": "🐛 Bug Fixes",
    "perf": "⚡ Performance",
    "docs": "📚 Documentation",
    "refactor": "♻️ Refactors",
}

def notes() -> None:
    try:
        last = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"], text=True).strip()
    except subprocess.CalledProcessError:
        last = "HEAD~50"
    commits = subprocess.check_output(["git", "log", f"{last}..HEAD", "--pretty=%s"], text=True).splitlines()
    buckets = defaultdict(list)
    for msg in commits:
        if ":" in msg:
            cat, body = msg.split(":", 1)
            buckets[CATEGORIES.get(cat.strip(), "🔧 Other")].append(f"- {body.strip()}")
    lines = [f"# Release Notes (since {last})\n"]
    for cat in CATEGORIES.values():
        if entries := buckets.get(cat):
            lines.extend([f"\n## {cat}"] + entries)
    Path("RELEASE_NOTES.md").write_text("\n".join(lines) + "\n")
    print("✅ RELEASE_NOTES.md generated.")

if __name__ == "__main__":
    notes()
