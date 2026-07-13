#!/usr/bin/env python3
"""Verify Dockerfile exposes the same port as settings.json."""

import json
import re
from pathlib import Path

def check() -> int:
    settings = json.loads(Path("settings.json").read_text())
    expected = settings["web"]["server"]["port"]
    dockerfile = Path("Dockerfile")
    if not dockerfile.exists():
        print("⚠️  No Dockerfile found.")
        return 0
    text = dockerfile.read_text()
    exposed = re.findall(r"EXPOSE\s+(\d+)", text)
    if str(expected) in exposed:
        print(f"✅ Dockerfile exposes {expected} (matches settings.json).")
        return 0
    print(f"❌ Dockerfile exposes {exposed or 'nothing'}; settings.json expects {expected}.")
    return 1

if __name__ == "__main__":
    import sys
    sys.exit(check())
