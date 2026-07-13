#!/usr/bin/env python3
"""Verify local branch name follows naming convention (feature/ fix/ chore/ docs/)."""

import re
import subprocess
import sys
from pathlib import Path

PATTERN = re.compile(r"^(main|master|release/.+|hotfix/.+|feature/.+|fix/.+|chore/.+|docs/.+)$")

def check() -> int:
    branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    if PATTERN.match(branch):
        print(f"✅ Branch name '{branch}' follows convention.")
        return 0
    print(f"❌ Branch '{branch}' violates naming convention.")
    print(f"   Allowed: main, master, release/*, hotfix/*, feature/*, fix/*, chore/*, docs/*")
    return 1

if __name__ == "__main__":
    sys.exit(check())
