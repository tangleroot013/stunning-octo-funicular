#!/usr/bin/env python3
"""Run only tests matching a pattern, or full suite if no args."""

import subprocess
import sys
from pathlib import Path

def run() -> int:
    pattern = sys.argv[1] if len(sys.argv) > 1 else ""
    cmd = ["pytest", "-v", "--tb=short"]
    if pattern:
        cmd += ["-k", pattern]
    return subprocess.run(cmd).returncode

if __name__ == "__main__":
    sys.exit(run())
