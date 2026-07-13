#!/usr/bin/env python3
"""Verify Makefile targets map to existing scripts and are syntactically valid."""

import re
import subprocess
import sys
from pathlib import Path

def validate() -> int:
    if not Path("Makefile").exists():
        print("❌ Makefile missing. Run: python scripts/auto_makefile.py")
        return 1
    text = Path("Makefile").read_text()
    targets = re.findall(r"^([a-zA-Z0-9_-]+):", text, re.MULTILINE)
    scripts = {p.stem.replace("_", "-") for p in Path("scripts").glob("*.py")}
    orphan = set(targets) - {"all", "help", "clean", "audit"} - scripts
    if orphan:
        print(f"⚠️  Makefile targets without scripts: {orphan}")
    result = subprocess.run(["make", "-n", "help"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Makefile syntax error:\\n{result.stderr}")
        return 1
    print(f"✅ Makefile valid ({len(targets)} targets, {len(scripts)} scripts).")
    return 0

if __name__ == "__main__":
    sys.exit(validate())
