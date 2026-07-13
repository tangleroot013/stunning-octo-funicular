#!/usr/bin/env python3
"""Inspect the built wheel for missing critical files and size anomalies."""

import json
import subprocess
import sys
import zipfile
from pathlib import Path

def inspect() -> int:
    data = json.loads(Path("settings.json").read_text())
    pkg = data["library"]["package_name"]
    wheels = list(Path("dist").glob("*.whl"))
    if not wheels:
        print("❌ No wheel found. Run: python -m build --wheel")
        return 1
    
    wheel = wheels[0]
    print(f"📦 {wheel.name}")
    with zipfile.ZipFile(wheel) as zf:
        files = zf.namelist()
        py_files = [f for f in files if f.endswith(".py")]
        print(f"   {len(files)} files, {len(py_files)} .py files")
        
        # Check for expected package
        expected_prefix = pkg.replace("_", "-")
        if not any(expected_prefix in f for f in files):
            print(f"⚠️  Wheel may be missing package '{pkg}'")
        
        # Check for tests in wheel
        if any("test" in f for f in files):
            print("⚠️  Tests included in wheel (should be excluded)")
            return 1
    
    size = wheel.stat().st_size / 1024
    print(f"   Size: {size:.1f} KB")
    if size > 500:
        print("⚠️  Wheel exceeds 500KB — consider slimming dependencies")
    return 0

if __name__ == "__main__":
    sys.exit(inspect())
