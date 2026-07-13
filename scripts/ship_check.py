#!/usr/bin/env python3
"""Dry-run ship.py validations without side effects."""

import json
import subprocess
from pathlib import Path

def check() -> int:
    if not Path("ship.py").exists():
        print("⚠️  ship.py not found.")
        return 0
    data = json.loads(Path("settings.json").read_text())
    ver = data["library"]["version"]
    tag = f"v{ver}"
    existing = subprocess.run(["git", "rev-parse", tag], capture_output=True)
    if existing.returncode == 0:
        print(f"❌ Tag {tag} already exists. Bump version first.")
        return 1
    print(f"✅ Ship check passed. Ready to tag {tag}.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(check())
