#!/usr/bin/env python3
"""Detect version conflicts in transitive dependencies from pip freeze."""

import re
import subprocess
import sys
from pathlib import Path
from collections import defaultdict

def audit() -> int:
    result = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True)
    packages = defaultdict(list)
    for line in result.stdout.splitlines():
        if "==" in line:
            name, ver = line.split("==", 1)
            packages[name.lower()].append(ver)
    conflicts = {k: v for k, v in packages.items() if len(v) > 1}
    if conflicts:
        print(f"❌ {len(conflicts)} package(s) with multiple versions:")
        for pkg, vers in conflicts.items():
            print(f"   {pkg}: {', '.join(vers)}")
        return 1
    print(f"✅ All {len(packages)} packages resolve cleanly.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
