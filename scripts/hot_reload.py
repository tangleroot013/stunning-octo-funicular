#!/usr/bin/env python3
"""Watch src/ and auto-restart FastAPI dev server on changes."""

import subprocess
import sys
import time
from pathlib import Path

def watch() -> None:
    mtimes = {}
    cmd = [sys.executable, "-m", "uvicorn", "src.main:app", "--reload"]
    proc = subprocess.Popen(cmd)
    try:
        while True:
            changed = False
            for py in Path("src").rglob("*.py"):
                m = py.stat().st_mtime
                if py in mtimes and mtimes[py] != m:
                    changed = True
                mtimes[py] = m
            if changed:
                proc.terminate()
                proc.wait()
                proc = subprocess.Popen(cmd)
                print("🔄 Reloaded")
            time.sleep(1)
    except KeyboardInterrupt:
        proc.terminate()

if __name__ == "__main__":
    watch()
