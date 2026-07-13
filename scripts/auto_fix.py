#!/usr/bin/env python3
"""Autonomous fix engine: run ruff --fix, black, isort, and pyupgrade in sequence."""

import subprocess
import sys
from pathlib import Path

FIXERS = [
    ("ruff", ["ruff", "check", "src", "scripts", "--fix"]),
    ("black", ["black", "src", "scripts"]),
    ("isort", ["isort", "src", "scripts"]),
    ("pyupgrade", [sys.executable, "-m", "pyupgrade", "--py311-plus", "--keep-runtime-typing"] + [str(p) for p in list(Path("src").rglob("*.py")) + list(Path("scripts").rglob("*.py"))]),
]

def fix() -> int:
    fixed = 0
    for name, cmd in FIXERS:
        print(f"\\n🔧 {name}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 or "reformatted" in result.stderr or "fixed" in result.stdout:
            print(f"   ✅ {name} complete")
            fixed += 1
        else:
            print(f"   ⚠️  {name}: {result.stderr[:200] if result.stderr else 'no changes'}")
    
    # Stage changes if any
    status = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True)
    if status.stdout.strip():
        subprocess.run(["git", "add", "-u"], capture_output=True)
        print(f"\\n📦 Staged {len(status.stdout.splitlines())} file(s)")
    
    print(f"\\n{'✅ All fixers applied' if fixed == len(FIXERS) else f'⚠️  {fixed}/{len(FIXERS)} fixers applied'}")
    return 0

if __name__ == "__main__":
    sys.exit(fix())
