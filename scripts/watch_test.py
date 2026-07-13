#!/usr/bin/env python3
"""Auto-run pytest whenever any .py file in src/ or tests/ changes (stat polling, zero deps)."""

import subprocess
import sys
import time
from pathlib import Path

def watch() -> None:
    mtimes = {}
    print("👁️  Watching src/ and tests/ ... Ctrl+C to stop")
    while True:
        changed = False
        for root in ("src", "tests"):
            for py in Path(root).rglob("*.py"):
                m = py.stat().st_mtime
                if py in mtimes and mtimes[py] != m:
                    changed = True
                mtimes[py] = m
        if changed:
            print("\\n🔄 Change detected — running pytest...")
            result = subprocess.run([sys.executable, "-m", "pytest", "-q", "--tb=short"])
            print(f"{'✅ PASS' if result.returncode == 0 else '❌ FAIL'}\\n{'─'*40}")
        time.sleep(0.5)

if __name__ == "__main__":
    try:
        watch()
    except KeyboardInterrupt:
        print("\\n👋 Stopped.")
