#!/usr/bin/env python3
"""Autonomous guardian: runs all checks, heals, warms, and reports on a schedule."""

import subprocess
import sys
import time
from pathlib import Path

CYCLE_SEC = 300  # 5 minutes

def guardian() -> None:
    print(f"🛡️  Autonomous Guardian started. Cycle: {CYCLE_SEC}s. Ctrl+C to stop.\\n")
    
    while True:
        cycle_start = time.time()
        timestamp = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\\n{'='*50}")
        print(f"🕐 Cycle: {timestamp}")
        print(f"{'='*50}")
        
        # Health check
        health = subprocess.run([sys.executable, "scripts/health_score.py"], capture_output=True)
        if health.returncode != 0:
            print("   🏥 Health low — running auto-heal...")
            subprocess.run([sys.executable, "scripts/auto_heal.py"], capture_output=True)
        
        # Warm caches
        subprocess.run([sys.executable, "scripts/auto_warm.py"], capture_output=True)
        
        # Generate reports
        subprocess.run([sys.executable, "scripts/omnibus_v3.py"], capture_output=True)
        subprocess.run([sys.executable, "scripts/metrics_emit.py"], capture_output=True)
        
        # Snapshot if needed
        if not Path(".last_snapshot").exists() or \
           time.time() - Path(".last_snapshot").stat().st_mtime > 3600:
            subprocess.run([sys.executable, "scripts/auto_snapshot.py"], capture_output=True)
            Path(".last_snapshot").touch()
        
        elapsed = time.time() - cycle_start
        print(f"\\n✅ Cycle complete in {elapsed:.1f}s. Sleeping {max(0, CYCLE_SEC - elapsed):.0f}s...")
        time.sleep(max(0, CYCLE_SEC - elapsed))

if __name__ == "__main__":
    try:
        guardian()
    except KeyboardInterrupt:
        print("\\n👋 Guardian stopped.")
