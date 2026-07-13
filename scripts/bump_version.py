#!/usr/bin/env python3
"""Bump patch version in settings.json, tag, and push."""

import json
import subprocess
import sys
from pathlib import Path

def bump() -> None:
    path = Path("settings.json")
    data = json.loads(path.read_text())
    ver = data["library"]["version"]
    major, minor, patch = map(int, ver.split("."))
    new_ver = f"{major}.{minor}.{patch + 1}"
    data["library"]["version"] = new_ver
    path.write_text(json.dumps(data, indent=2) + "\n")
    subprocess.run(["git", "add", "settings.json"], check=True)
    subprocess.run(["git", "commit", "-m", f"chore: bump version {ver} → {new_ver}"], check=True)
    subprocess.run(["git", "tag", f"v{new_ver}"], check=True)
    print(f"✅ Tagged v{new_ver}. Run 'git push && git push --tags' when ready.")

if __name__ == "__main__":
    bump()
