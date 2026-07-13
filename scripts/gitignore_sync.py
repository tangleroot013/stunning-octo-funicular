#!/usr/bin/env python3
"""Sync .gitignore from settings.json workspace.ignore_patterns.gitignore."""

import json
from pathlib import Path

def sync() -> None:
    data = json.loads(Path("settings.json").read_text())
    patterns = data["workspace"]["ignore_patterns"]["gitignore"]
    header = "# Auto-generated from settings.json\n"
    Path(".gitignore").write_text(header + "\n".join(patterns) + "\n")
    print("✅ .gitignore synced.")

if __name__ == "__main__":
    sync()
