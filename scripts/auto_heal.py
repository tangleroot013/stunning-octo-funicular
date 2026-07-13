#!/usr/bin/env python3
"""Autonomous healing: detect failures, apply fixes, retry, and escalate."""

import subprocess
import sys
from pathlib import Path

HEAL_STEPS = [
    ("fix formatting", ["python", "scripts/auto_fix.py"]),
    ("sync ignores", ["python", "scripts/gitignore_sync.py"]),
    ("purge caches", ["python", "scripts/cache_purge.py"]),
    ("warm caches", ["python", "scripts/auto_warm.py"]),
]

def heal() -> int:
    print("🏥 Autonomous healing starting...\\n")
    
    # Run full check
    result = subprocess.run([sys.executable, "scripts/omnibus_v3.py"], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Already healthy. No healing needed.")
        return 0
    
    print(f"⚠️  Health check failed. Attempting fixes...\\n")
    
    for name, cmd in HEAL_STEPS:
        print(f"🔧 Trying: {name}...")
        subprocess.run(cmd, capture_output=True)
        # Re-check
        result = subprocess.run([sys.executable, "scripts/omnibus_v3.py"], capture_output=True)
        if result.returncode == 0:
            print(f"\\n✅ Healed by: {name}")
            return 0
    
    print(f"\\n❌ Autonomous healing failed. Manual intervention required.")
    print(f"   Run: python scripts/omnibus_v3.py")
    return 1

if __name__ == "__main__":
    sys.exit(heal())
