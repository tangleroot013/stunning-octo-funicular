#!/usr/bin/env python3
"""Detect functools.partial usage that could be replaced by default arguments."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == "partial":
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "functools":
                        print(f"🔍 {py}:{node.lineno} functools.partial — consider default args for clarity")
                        hits += 1
    if hits:
        print(f"\n⚠️  {hits} functools.partial usage(s). Review for simplification.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
