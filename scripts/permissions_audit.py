#!/usr/bin/env python3
"""Audit file permissions for world-writable or executable files in the repo."""

import os
import stat
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for f in Path(".").rglob("*"):
        if f.is_file() and ".git" not in str(f):
            mode = f.stat().st_mode
            if mode & stat.S_IWOTH:
                print(f"🚨 {f}: world-writable ({oct(mode)[-3:]})")
                hits += 1
            if f.suffix == ".py" and mode & stat.S_IXUSR:
                if not f.read_bytes().startswith(b"#!"):
                    print(f"⚠️  {f}: executable without shebang ({oct(mode)[-3:]})")
                    hits += 1
    if hits:
        print(f"\n❌ {hits} permission issue(s). Run: chmod o-w <file> or chmod -x <file>")
        return 1
    print("✅ File permissions secure.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
