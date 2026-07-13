#!/usr/bin/env python3
"""Hunt flaky tests by running them N times with randomized order."""

import subprocess
import sys
from pathlib import Path

def hunt(target: str, runs: int = 20) -> int:
    fails = 0
    for i in range(runs):
        seed = i * 42
        cmd = [sys.executable, "-m", "pytest", target, "-x", "-q", f"--randomly-seed={seed}"]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            fails += 1
            print(f"❌ Run {i+1}/{runs} (seed {seed}) FAILED")
            print(result.stdout.decode()[-500:] if result.stdout else "")
        else:
            print(f"✅ Run {i+1}/{runs} (seed {seed}) passed")
    print(f"\n{'🎯 FLAKY' if fails > 0 else '✅ STABLE'}: {fails}/{runs} failures")
    return 1 if fails > runs * 0.1 else 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: flake_hunter.py <test_file.py> [runs=20]")
        sys.exit(1)
    sys.exit(hunt(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 20))
