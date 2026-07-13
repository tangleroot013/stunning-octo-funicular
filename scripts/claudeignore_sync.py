#!/usr/bin/env python3
"""Sync .claudeignore from settings.json workspace.ignore_patterns.claudeignore."""

import json
from pathlib import Path

def sync() -> None:
    data = json.loads(Path("settings.json").read_text())
    patterns = data["workspace"]["ignore_patterns"]["claudeignore"]
    header = "# Auto-generated from settings.json\n"
    Path(".claudeignore").write_text(header + "\n".join(patterns) + "\n")
    print("✅ .claudeignore synced.")

if __name__ == "__main__":
    sync()
