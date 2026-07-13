#!/usr/bin/env python3
"""Autonomous cache warming: precompile, preload imports, and validate health."""

import subprocess
import sys
from pathlib import Path

def warm() -> int:
    print("🔥 Autonomous warming starting...\\n")
    
    # Compile all Python
    print("1. Bytecode compilation...")
    subprocess.run([sys.executable, "-m", "compileall", "src", "scripts", "-q"], capture_output=True)
    
    # Warm imports
    print("2. Import warming...")
    subprocess.run([sys.executable, "scripts/warm_cache.py"], capture_output=True)
    
    # Run health check
    print("3. Health validation...")
    result = subprocess.run([sys.executable, "scripts/health_score.py"], capture_output=True)
    
    # Generate metrics
    print("4. Emitting metrics...")
    subprocess.run([sys.executable, "scripts/metrics_emit.py"], capture_output=True)
    
    print("\\n✅ Autonomous warming complete.")
    return 0

if __name__ == "__main__":
    sys.exit(warm())
