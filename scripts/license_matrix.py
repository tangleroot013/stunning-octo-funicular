#!/usr/bin/env python3
"""Build license compatibility matrix: flag GPL/AGPL/SSPL in proprietary projects."""

import subprocess
import sys
from pathlib import Path

COPYLEFT = {"GPL", "AGPL", "SSPL", "EUPL", "OSL", "CPL", "MPL"}
PERMISSIVE = {"MIT", "Apache", "BSD", "ISC", "PSF", "Unlicense", "WTFPL", "CC0"}
PROPRIETARY = True  # Set False for open-source projects

def audit() -> int:
    result = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True)
    packages = [line.split("==")[0] for line in result.stdout.splitlines() if "==" in line]
    
    flagged = []
    unknown = []
    
    for pkg in packages:
        meta = subprocess.run([sys.executable, "-m", "pip", "show", pkg], capture_output=True, text=True)
        lic = ""
        for line in meta.stdout.splitlines():
            if line.startswith("License:"):
                lic = line.split(":", 1)[1].strip()
        
        if any(c in lic for c in COPYLEFT):
            flagged.append((pkg, lic))
        elif not any(p in lic for p in PERMISSIVE):
            unknown.append((pkg, lic))
    
    print("# License Compatibility Matrix\n")
    print(f"{'Package':<30} {'License':<25} {'Risk'}")
    print("-" * 70)
    
    for pkg, lic in flagged:
        print(f"{pkg:<30} {lic:<25} 🔴 BLOCKING")
    for pkg, lic in unknown:
        print(f"{pkg:<30} {lic:<25} 🟡 REVIEW")
    
    if flagged and PROPRIETARY:
        print(f"\n❌ {len(flagged)} copyleft package(s) incompatible with proprietary distribution.")
        return 1
    if unknown:
        print(f"\n⚠️  {len(unknown)} package(s) with unknown license status.")
    print("\n✅ License matrix clean.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
