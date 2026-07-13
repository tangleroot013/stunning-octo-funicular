#!/usr/bin/env python3
"""Autonomous file watcher: run tests on change, auto-fix failures, and notify."""

import subprocess
import sys
import time
from pathlib import Path

def watch() -> None:
    mtimes = {}
    print("👁️  Autonomous watch mode. Ctrl+C to stop.\\n")
    
    while True:
        changed = False
        for root in ("src", "tests", "scripts"):
            for py in Path(root).rglob("*.py"):
                m = py.stat().st_mtime
                if py in mtimes and mtimes[py] != m:
                    changed = True
                mtimes[py] = m
        
        if changed:
            print(f"🔄 Change detected at {__import__('datetime').datetime.now().strftime('%H:%M:%S')}")
            
            # Auto-fix first
            subprocess.run([sys.executable, "scripts/auto_fix.py"], capture_output=True)
            
            # Run tests
            result = subprocess.run([sys.executable, "scripts/test_parallel.py"], capture_output=True, text=True)
            ok = result.returncode == 0
            
            # Notify
            status = "✅ PASS" if ok else "❌ FAIL"
            print(f"   {status}")
            
            # Try auto-heal on failure
            if not ok:
                print("   🏥 Attempting auto-heal...")
                subprocess.run([sys.executable, "scripts/auto_heal.py"], capture_output=True)
            
            print(f"   {'─'*40}")
        
        time.sleep(0.5)

if __name__ == "__main__":
    try:
        watch()
    except KeyboardInterrupt:
        print("\\n👋 Watch stopped.")
