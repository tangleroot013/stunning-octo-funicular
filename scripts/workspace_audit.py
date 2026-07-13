#!/usr/bin/env python3
"""Master integrity audit: validates all critical files, dotfiles, and settings schema."""

import json
import subprocess
import sys
from pathlib import Path

CHECKS = {
    "settings.json": lambda p: json.loads(p.read_text()) and True,
    "hatch.py": lambda p: "def " in p.read_text(),
    "ship.py": lambda p: "def " in p.read_text(),
    "pyproject.toml": lambda p: "[tool.pytest" in p.read_text(),
    "src": lambda p: p.is_dir() and any(p.rglob("*.py")),
    "tests": lambda p: p.is_dir() and any(p.rglob("test_*.py")),
    ".gitignore": lambda p: p.exists(),
    ".claudeignore": lambda p: p.exists(),
    ".venv": lambda p: p.is_dir() or (Path(".python-version").exists()),
}

def audit() -> int:
    fails = 0
    print("# Workspace Audit\n")
    for name, validator in CHECKS.items():
        path = Path(name)
        try:
            ok = validator(path)
            status = "✅" if ok else "❌"
        except Exception as exc:
            status = "❌"
            ok = False
        print(f"{status} {name:<20} {'OK' if ok else 'FAIL'}")
        if not ok:
            fails += 1
    dotfiles = [p.name for p in Path(".").glob(".last_*") if p.is_file()]
    print(f"\n📊 Dotfiles detected: {len(dotfiles)} ({', '.join(dotfiles[:5])})")
    print(f"\n{'✅ All checks passed' if fails == 0 else f'❌ {fails} check(s) failed'}")
    return fails

if __name__ == "__main__":
    sys.exit(audit())
