#!/usr/bin/env python3
"""Install scripts/hook_guard.py as the actual .git/hooks/pre-commit hook."""

import shutil
from pathlib import Path

def install() -> None:
    src = Path("scripts/hook_guard.py")
    dest = Path(".git/hooks/pre-commit")
    if not src.exists():
        print("❌ hook_guard.py not found.")
        return
    shutil.copy(src, dest)
    dest.chmod(0o755)
    print(f"✅ Installed {src} → {dest}")

if __name__ == "__main__":
    install()
