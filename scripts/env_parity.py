#!/usr/bin/env python3
"""Compare development vs production environment variables from settings.json."""

import json
from pathlib import Path

def parity() -> int:
    data = json.loads(Path("settings.json").read_text())
    dev = data.get("ci", {}).get("environments", {}).get("development", {})
    prod = data.get("ci", {}).get("environments", {}).get("production", {})
    
    dev_only = set(dev) - set(prod)
    prod_only = set(prod) - set(dev)
    mismatched = {k for k in (set(dev) & set(prod)) if dev[k] != prod[k]}
    
    if dev_only:
        print(f"⚠️  Dev-only vars: {dev_only}")
    if prod_only:
        print(f"⚠️  Prod-only vars: {prod_only}")
    if mismatched:
        print(f"⚠️  Value mismatches: {mismatched}")
        for k in mismatched:
            print(f"   {k}: dev={dev[k]} vs prod={prod[k]}")
    if not any((dev_only, prod_only, mismatched)):
        print("✅ Dev and prod environments are perfectly aligned.")
        return 0
    return 1

if __name__ == "__main__":
    import sys
    sys.exit(parity())
