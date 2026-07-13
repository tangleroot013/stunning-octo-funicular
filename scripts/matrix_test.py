#!/usr/bin/env python3
"""Run pytest across a local version matrix."""

import subprocess
import sys
from pathlib import Path

VERSIONS = ["3.11", "3.12"]

def run_version(py: str) -> bool:
    print(f"\n🔷 Python {py}")
    try:
        subprocess.run([f"python{py}", "-m", "pytest", "-q"], check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main() -> int:
    results = {v: run_version(v) for v in VERSIONS}
    print("\n" + "=" * 40)
    for v, ok in results.items():
        print(f"{'✅' if ok else '❌'} {v}")
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    sys.exit(main())
