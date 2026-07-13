#!/usr/bin/env python3
"""List all semver tags with gap analysis for missing patch versions."""

import subprocess
import re
from pathlib import Path

def list_tags() -> None:
    result = subprocess.run(
        ["git", "tag", "--list", "v*"],
        capture_output=True, text=True
    )
    tags = sorted(result.stdout.splitlines())
    
    versions = []
    for t in tags:
        m = re.match(r"v(\d+)\.(\d+)\.(\d+)", t)
        if m:
            versions.append(tuple(map(int, m.groups())))
    
    if not versions:
        print("ℹ️  No semver tags found.")
        return
    
    print("# Tag History\n")
    for v in versions[-10:]:
        print(f"v{v[0]}.{v[1]}.{v[2]}")
    
    # Gap detection
    latest = versions[-1]
    print(f"\nLatest: v{latest[0]}.{latest[1]}.{latest[2]}")
    
    # Check settings.json alignment
    data = json.loads(Path("settings.json").read_text())
    current = data["library"]["version"]
    if current != f"{latest[0]}.{latest[1]}.{latest[2]}":
        print(f"⚠️  settings.json ({current}) != latest tag")

if __name__ == "__main__":
    import json
    list_tags()
