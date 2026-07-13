#!/usr/bin/env python3
"""Time each stage of the build (lint, test, package) and identify the slowest."""

import subprocess
import time
import sys
from pathlib import Path

STAGES = [
    ("lint", ["ruff", "check", "src"]),
    ("test", [sys.executable, "-m", "pytest", "-q"]),
    ("package", [sys.executable, "-m", "build", "--wheel"]),
]

def time_stages() -> int:
    times = []
    for name, cmd in STAGES:
        print(f"\\n⏱️  {name}...")
        t0 = time.perf_counter()
        result = subprocess.run(cmd, capture_output=True)
        elapsed = (time.perf_counter() - t0)
        times.append((name, elapsed, result.returncode))
        print(f"   {elapsed:.2f}s {'✅' if result.returncode == 0 else '❌'}")
    
    print(f"\\n{'='*40}")
    slowest = max(times, key=lambda x: x[1])
    for name, elapsed, rc in sorted(times, key=lambda x: -x[1]):
        bar = "█" * int(elapsed / slowest[1] * 20)
        print(f"{name:10} {elapsed:6.2f}s {bar}")
    return 1 if any(rc != 0 for _, _, rc in times) else 0

if __name__ == "__main__":
    sys.exit(time_stages())
