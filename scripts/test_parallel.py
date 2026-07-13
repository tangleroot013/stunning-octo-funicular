#!/usr/bin/env python3
"""Run pytest with xdist if available, fallback to sequential."""

import subprocess
import sys

def run() -> int:
    try:
        import xdist  # noqa: F401
        cmd = [sys.executable, "-m", "pytest", "-n", "auto", "-q"]
        print("⚡ Running tests in parallel (xdist detected)")
    except ImportError:
        cmd = [sys.executable, "-m", "pytest", "-q"]
        print("🐢 Running tests sequentially (install pytest-xdist for parallel)")
    return subprocess.run(cmd).returncode

if __name__ == "__main__":
    sys.exit(run())
