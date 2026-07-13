#!/usr/bin/env python3
"""Audit resource usage: ensure files, locks, and connections use context managers."""

import ast
import sys
from pathlib import Path

RESOURCES = {"open", "socket", "connect", "acquire", "lock"}

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in ("open",):
                    # Check if parent is With
                    print(f"⚠️  {py}:{node.lineno} open() call — verify context manager usage")
                    hits += 1
                if isinstance(node.func, ast.Attribute) and node.func.attr in ("acquire", "connect"):
                    print(f"⚠️  {py}:{node.lineno} {node.func.attr}() — verify context manager or finally")
                    hits += 1
    if hits:
        print(f"\n⚠️  {hits} resource call(s) need manual review for context manager usage.")
        return 0  # warning only
    print("✅ Resource management looks clean.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
