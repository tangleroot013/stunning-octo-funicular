#!/usr/bin/env python3
"""Run the full CI pipeline locally: lint, test, coverage, security scan."""

import subprocess
import sys
from pathlib import Path

STAGES = [
    ("Lint", ["python", "scripts/lint_report.py"]),
    ("Test", ["python", "scripts/test_parallel.py"]),
    ("Coverage", ["python", "scripts/alert_threshold.py"]),
    ("Security", ["python", "scripts/secret_scan.py"]),
    ("Deps", ["python", "scripts/audit_deps.py"]),
]

def run() -> int:
    failed = []
    for name, cmd in STAGES:
        print(f"\n{'='*40}\n🔷 Stage: {name}\n{'='*40}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            failed.append(name)
    print(f"\n{'='*40}\n{'✅ All stages passed' if not failed else f'❌ Failed: {', '.join(failed)}'}\n{'='*40}")
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(run())
