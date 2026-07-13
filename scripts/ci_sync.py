#!/usr/bin/env python3
"""Validate .github/workflows/ci.yml stages match settings.json ci.stages exactly."""

import json
import re
import sys
from pathlib import Path

def validate() -> int:
    data = json.loads(Path("settings.json").read_text())
    expected = data.get("ci", {}).get("stages", [])
    ci = Path(".github/workflows/ci.yml")
    if not ci.exists():
        print("❌ .github/workflows/ci.yml missing")
        return 1
    text = ci.read_text()
    found = re.findall(r"^\\s+(-\\s*name:\\s*(.+))", text, re.MULTILINE)
    names = [n.strip() for _, n in found]
    missing = set(expected) - set(names)
    extra = set(names) - set(expected)
    if missing:
        print(f"❌ CI missing stages: {missing}")
    if extra:
        print(f"⚠️  CI has extra stages: {extra}")
    if not missing and not extra:
        print(f"✅ CI sync: {len(expected)} stage(s) match")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(validate())
