#!/usr/bin/env python3
"""Autonomous cleanup: prune branches, purge caches, archive logs, and report."""

import subprocess
import sys
from pathlib import Path

def prune() -> int:
    print("🧹 Autonomous cleanup starting...\\n")
    
    # Prune merged branches
    print("1. Pruning merged branches...")
    subprocess.run([sys.executable, "scripts/branch_cleanup.py"], capture_output=True)
    
    # Purge caches
    print("2. Purging caches...")
    subprocess.run([sys.executable, "scripts/cache_purge.py"], capture_output=True)
    
    # Archive old logs
    print("3. Archiving logs...")
    subprocess.run([sys.executable, "scripts/log_archive.py"], capture_output=True)
    
    # Prune remote branches
    print("4. Pruning remote tracking...")
    subprocess.run([sys.executable, "scripts/remote_prune.py"], capture_output=True)
    
    # Check disk
    print("5. Checking disk...")
    result = subprocess.run([sys.executable, "scripts/disk_budget.py"], capture_output=True)
    
    print("\\n✅ Autonomous cleanup complete.")
    return 0

if __name__ == "__main__":
    sys.exit(prune())
