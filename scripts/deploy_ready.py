#!/usr/bin/env python3
"""Gatekeeper: fail if any critical check fails before deploy."""

import subprocess
import sys
from pathlib import Path

GATES = [
    ("health_score", [sys.executable, "scripts/health_score.py"]),
    ("pypi_slot", [sys.executable, "scripts/pypi_check.py"]),
    ("tests", [sys.executable, "scripts/test_parallel.py"]),
    ("secrets", [sys.executable, "scripts/secret_scan.py"]),
    ("version_bump", [sys.executable, "scripts/ship_check.py"]),
]

def ready() -> int:
    print("🚦 Deploy Readiness Check\n")
    for name, cmd in GATES:
        result = subprocess.run(cmd, capture_output=True)
        ok = result.returncode == 0
        print(f"  {'✅' if ok else '❌'} {name}")
        if not ok:
            print(f"     Deploy BLOCKED.")
            return 1
    print("\n🚀 ALL GATES PASS. Ready to deploy.")
    return 0

if __name__ == "__main__":
    sys.exit(ready())
