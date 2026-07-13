#!/usr/bin/env python3
"""Verify all executable scripts have correct shebangs and no CRLF line endings."""

import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for script in Path("scripts").rglob("*.py"):
        if not script.stat().st_mode & 0o111:
            continue  # not executable
        
        text = script.read_bytes()
        if b"\\r\\n" in text:
            print(f"❌ {script.name}: CRLF line endings")
            hits += 1
        
        first = text.split(b"\\n")[0] if b"\\n" in text else text
        if not first.startswith(b"#!"):
            print(f"❌ {script.name}: missing shebang (is executable)")
            hits += 1
        elif b"python3" not in first and b"python" not in first:
            print(f"⚠️  {script.name}: unusual shebang: {first.decode(errors='ignore').strip()}")
    
    if hits:
        print(f"\n❌ {hits} shebang/line-ending issue(s).")
        return 1
    print("✅ All executable scripts properly formatted.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
