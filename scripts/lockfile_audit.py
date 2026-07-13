#!/usr/bin/env python3
"""Flag lockfiles that exist on disk but are gitignored (sync drift)."""

import subprocess
import sys
from pathlib import Path

LOCKFILES = ("package-lock.json", "yarn.lock", "Pipfile.lock", "poetry.lock", "Cargo.lock")

def audit() -> int:
    ignored = subprocess.check_output(["git", "check-ignore"] + list(LOCKFILES), text=True, errors="ignore").splitlines()
    existing = [f for f in LOCKFILES if Path(f).exists()]
    drift = set(existing) & set(ignored)
    if drift:
        print(f"❌ Lockfiles exist but are gitignored: {drift}")
        print("   Run: git rm --cached <file> && rm <file>  (or remove from .gitignore)")
        return 1
    print("✅ Lockfiles and .gitignore are in sync.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
