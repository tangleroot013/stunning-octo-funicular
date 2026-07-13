#!/usr/bin/env python3
"""Mirror push to a backup remote (reads MIRROR_REMOTE from env)."""

import os
import subprocess
import sys
from pathlib import Path

def sync() -> int:
    mirror = os.environ.get("MIRROR_REMOTE")
    if not mirror:
        print("ℹ️  Set MIRROR_REMOTE env var to enable mirroring.")
        return 0
    
    # Check if remote exists
    remotes = subprocess.check_output(["git", "remote"], text=True).splitlines()
    if "mirror" not in remotes:
        subprocess.run(["git", "remote", "add", "mirror", mirror], check=True)
        print(f"🔌 Added mirror remote: {mirror}")
    
    result = subprocess.run(["git", "push", "mirror", "--all", "--force"], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Mirror sync complete.")
        return 0
    print(f"❌ Mirror sync failed: {result.stderr}")
    return 1

if __name__ == "__main__":
    sys.exit(sync())
