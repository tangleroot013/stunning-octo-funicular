#!/usr/bin/env python3
"""Parse requirements.txt and draw a flat dependency tree via pipdeptree."""

import subprocess
import sys
from pathlib import Path

def tree() -> int:
    if not Path("requirements.txt").exists():
        print("⚠️  No requirements.txt found.")
        return 0
    result = subprocess.run([sys.executable, "-m", "pipdeptree"], capture_output=True, text=True)
    if result.returncode != 0:
        print("pipdeptree not installed. Run: pip install pipdeptree")
        return 1
    Path("DEP_TREE.txt").write_text(result.stdout)
    print("✅ DEP_TREE.txt written.")
    return 0

if __name__ == "__main__":
    sys.exit(tree())
