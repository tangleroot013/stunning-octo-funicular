#!/usr/bin/env python3
"""Validate settings.json structure and flag stale keys."""

import json
import sys
from pathlib import Path

REQUIRED_TOP_LEVEL = {
    "repository", "github", "ci", "web", "library", "testing", "workspace"
}

def validate(path: Path = Path("settings.json")) -> int:
    data = json.loads(path.read_text())
    missing = REQUIRED_TOP_LEVEL - data.keys()
    if missing:
        print(f"❌ Missing sections: {missing}")
        return 1
    if "token" in data.get("github", {}) and "ghp_" in data["github"]["token"]:
        print("🚨 Real GitHub token detected in settings.json!")
        return 1
    print("✅ settings.json is structurally sound.")
    return 0

if __name__ == "__main__":
    sys.exit(validate())
