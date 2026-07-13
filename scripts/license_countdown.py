#!/usr/bin/env python3
"""Audit installed packages for viral/copyleft licenses (GPL, AGPL, etc.)."""

import subprocess
import sys
from pathlib import Path

VIRAL = {"GPL", "AGPL", "SSPL", "EUPL"}
PERMISSIVE = {"MIT", "Apache", "BSD", "ISC", "PSF"}

def audit() -> int:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        capture_output=True, text=True
    )
    packages = [line.split("==")[0] for line in result.stdout.splitlines() if "==" in line]
    flagged = []
    for pkg in packages:
        meta = subprocess.run(
            [sys.executable, "-m", "pip", "show", pkg],
            capture_output=True, text=True
        )
        lic = ""
        for line in meta.stdout.splitlines():
            if line.startswith("License:"):
                lic = line.split(":", 1)[1].strip()
        if any(v in lic for v in VIRAL):
            flagged.append(f"{pkg} ({lic})")
        elif not any(p in lic for p in PERMISSIVE):
            flagged.append(f"{pkg} ({lic}) [unknown]")
    if flagged:
        print(f"⚠️  {len(flagged)} package(s) with restrictive/unknown licenses:")
        for f in flagged:
            print(f"   {f}")
        return 1
    print(f"✅ All {len(packages)} packages use permissive licenses.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
