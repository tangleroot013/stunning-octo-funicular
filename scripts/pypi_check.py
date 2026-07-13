#!/usr/bin/env python3
"""Check if current package version already exists on PyPI."""

import json
import sys
from urllib.request import urlopen
from pathlib import Path

def check() -> int:
    data = json.loads(Path("settings.json").read_text())
    pkg = data["library"]["package_name"].replace("_", "-")
    ver = data["library"]["version"]
    try:
        urlopen(f"https://pypi.org/pypi/{pkg}/{ver}/json", timeout=5)
        print(f"❌ Version {ver} already published to PyPI.")
        return 1
    except Exception:
        print(f"✅ Version {ver} is available for release.")
        return 0

if __name__ == "__main__":
    sys.exit(check())
