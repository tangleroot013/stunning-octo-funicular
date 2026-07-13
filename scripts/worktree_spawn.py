#!/usr/bin/env python3
"""Create a git worktree for a new feature branch to enable parallel development."""

import subprocess
import sys
from pathlib import Path

def spawn(branch: str) -> int:
    base = Path(f"../{Path('.').resolve().name}-{branch}")
    if base.exists():
        print(f"❌ {base} already exists.")
        return 1
    subprocess.run(["git", "worktree", "add", str(base), "-b", branch], check=True)
    print(f"✅ Worktree created: {base}")
    print(f"   cd {base} && python scripts/venv_check.py")
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: worktree_spawn.py <feature-branch-name>")
        sys.exit(1)
    sys.exit(spawn(sys.argv[1]))
