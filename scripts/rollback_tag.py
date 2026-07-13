#!/usr/bin/env python3
"""Tag current HEAD as rollback-point before risky operations."""

import subprocess
from datetime import datetime
from pathlib import Path

def tag() -> None:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tag_name = f"rollback-{stamp}"
    subprocess.run(["git", "tag", "-a", tag_name, "-m", f"Pre-change rollback point {stamp}"], check=True)
    print(f"🏷️  Tagged {tag_name}")
    print(f"   Recover with: git reset --hard {tag_name}")

if __name__ == "__main__":
    tag()
