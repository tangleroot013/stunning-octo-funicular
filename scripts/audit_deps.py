#!/usr/bin/env python3
"""Audit requirements files for dangerous patterns."""

import re
from pathlib import Path

DANGEROUS = re.compile(r"^(git\+http|git\+ssh|\.|/|http://)", re.IGNORECASE)
UNPINNED = re.compile(r"^[a-z0-9_-]+$", re.IGNORECASE)

def audit(path: Path) -> list[str]:
    issues = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if DANGEROUS.match(line):
            issues.append(f"Suspicious source: {line}")
        if UNPINNED.match(line):
            issues.append(f"Unpinned package: {line}")
    return issues

def main() -> None:
    all_ok = True
    for req in Path(".").glob("requirements*.txt"):
        if bad := audit(req):
            print(f"⚠️  {req}:")
            for b in bad:
                print(f"   - {b}")
            all_ok = False
    if all_ok:
        print("✅ All requirements files look clean.")

if __name__ == "__main__":
    main()
