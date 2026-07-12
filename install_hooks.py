#!/usr/bin/env python3
"""
install_hooks.py — wires a git pre-push hook that runs the venv's pytest
before any push reaches GitHub, regardless of whether ship.py was used.
"""
import os
import stat
from pathlib import Path

PROJ = Path(__file__).resolve().parent
HOOK_PATH = PROJ / ".git" / "hooks" / "pre-push"

HOOK_SCRIPT = """#!/usr/bin/env bash
set -e
cd "$(git rev-parse --show-toplevel)"

if [ -x ".venv/bin/python" ]; then
  PY=".venv/bin/python"
else
  PY="python3"
fi

echo "[pre-push] running pytest before allowing push..."
"$PY" -m pytest -q
echo "[pre-push] tests passed, proceeding with push"
"""

def main():
    if not (PROJ / ".git").exists():
        raise SystemExit(f"[error] {PROJ} is not a git repo")

    HOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    HOOK_PATH.write_text(HOOK_SCRIPT)

    st = os.stat(HOOK_PATH)
    os.chmod(HOOK_PATH, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    print(f"[installed] {HOOK_PATH}")
    print("Any `git push` from this repo now runs pytest first and blocks on failure.")
    print("Bypass in an emergency with: git push --no-verify")

if __name__ == "__main__":
    main()
