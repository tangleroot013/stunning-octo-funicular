#!/usr/bin/env python3
"""Find and kill stale Python/pytest processes that may be hanging from crashed tests."""

import subprocess
import sys
from pathlib import Path

def hunt() -> int:
    result = subprocess.run(
        ["ps", "aux"],
        capture_output=True, text=True
    )
    pids = []
    for line in result.stdout.splitlines():
        if any(x in line for x in ("pytest", "python -m pytest", "python3 -m pytest")):
            if "grep" not in line and "zombie_hunter" not in line:
                parts = line.split()
                pid = parts[1]
                time = parts[9]  # CPU time column
                pids.append((pid, time, " ".join(parts[10:])[:60]))
    
    if not pids:
        print("✅ No stale pytest processes found.")
        return 0
    
    print(f"⚠️  {len(pids)} pytest process(es) running:")
    for pid, time, cmd in pids:
        print(f"   PID {pid} (CPU {time}) {cmd}")
    
    confirm = input("\\nKill all? [y/N]: ").strip().lower()
    if confirm == "y":
        for pid, _, _ in pids:
            subprocess.run(["kill", "-9", pid], capture_output=True)
        print("💀 Terminated.")
    return 0

if __name__ == "__main__":
    sys.exit(hunt())
