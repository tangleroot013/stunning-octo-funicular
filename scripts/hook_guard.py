#!/usr/bin/env python3
"""Git pre-commit hook: block secrets and enforce staged hatch.py."""

import json
import subprocess
import sys
from pathlib import Path

def staged_files() -> list[str]:
    out = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True)
    return out.strip().splitlines()

def block_secrets() -> bool:
    settings = Path("settings.json")
    if not settings.exists():
        return True
    data = json.loads(settings.read_text())
    token = data.get("github", {}).get("token", "")
    if "ghp_" in token and "PLACEHOLDER" not in token:
        print("🚨 COMMIT BLOCKED: Real GitHub token in settings.json")
        return False
    return True

def block_unstaged_core() -> bool:
    if "hatch.py" in staged_files():
        unstaged = subprocess.check_output(["git", "diff", "--name-only"], text=True)
        if "hatch.py" in unstaged.splitlines():
            print("🚨 COMMIT BLOCKED: hatch.py has unstaged changes. Stage everything.")
            return False
    return True

if __name__ == "__main__":
    ok = block_secrets() and block_unstaged_core()
    sys.exit(0 if ok else 1)
