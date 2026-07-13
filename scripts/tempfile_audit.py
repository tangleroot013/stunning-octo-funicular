#!/usr/bin/env python3
"""Detect hardcoded /tmp paths and insecure tempfile usage."""

import ast
import re
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        text = py.read_text()
        tree = ast.parse(text)
        
        # Check string literals for /tmp
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if "/tmp" in node.value or "C:\\\\Windows\\\\Temp" in node.value:
                    print(f"🚨 {py}:{node.lineno} hardcoded temp path: {node.value[:40]}")
                    print(f"   Use: tempfile.mkstemp() or tempfile.TemporaryDirectory()")
                    hits += 1
        
        # Check for mktemp (insecure)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == "mktemp":
                    print(f"🚨 {py}:{node.lineno} tempfile.mktemp() — race condition vulnerability")
                    print(f"   Use: tempfile.mkstemp() instead")
                    hits += 1
    if hits:
        print(f"\n❌ {hits} insecure tempfile usage(s).")
        return 1
    print("✅ Tempfile usage secure.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
