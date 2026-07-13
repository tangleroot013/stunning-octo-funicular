#!/usr/bin/env python3
"""Scan pytest output for deprecation warnings and emit a report."""

import re
from pathlib import Path

def scan() -> None:
    log = Path("pytest.log")
    if not log.exists():
        print("⚠️  No pytest.log found. Run: pytest -W always --log-file=pytest.log")
        return
    warnings = []
    for line in log.read_text().splitlines():
        if "DeprecationWarning" in line or "PendingDeprecationWarning" in line:
            warnings.append(line.strip())
    if warnings:
        Path("DEPRECATION_REPORT.md").write_text("\n".join(["# Deprecation Warnings", ""] + [f"- {w}" for w in warnings[:50]]))
        print(f"⚠️  {len(warnings)} deprecation warnings found. See DEPRECATION_REPORT.md")
    else:
        print("✅ No deprecation warnings.")

if __name__ == "__main__":
    scan()
