#!/usr/bin/env python3
"""Validate .env file against required keys declared in settings.json."""

import json
from pathlib import Path

def validate() -> int:
    data = json.loads(Path("settings.json").read_text())
    required = set(data.get("ci", {}).get("environments", {}).get("production", {}).keys())
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  No .env file found.")
        return 0
    present = {k for k, _ in (line.split("=", 1) for line in env_file.read_text().splitlines() if "=" in line and not line.startswith("#"))}
    missing = required - present
    if missing:
        print(f"❌ Missing env vars: {missing}")
        return 1
    print("✅ All required env vars present.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(validate())
