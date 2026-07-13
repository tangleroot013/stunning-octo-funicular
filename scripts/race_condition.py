#!/usr/bin/env python3
"""Detect TOCTOU and race condition patterns: check-then-act sequences."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Look for existence check followed by action
                if isinstance(node.test, ast.Call):
                    if isinstance(node.test.func, ast.Attribute):
                        if node.test.func.attr in ("exists", "isfile", "isdir", "can_access"):
                            # Check if body contains operation on same path
                            if node.body:
                                for stmt in node.body:
                                    for child in ast.walk(stmt):
                                        if isinstance(child, ast.Call):
                                            if isinstance(child.func, ast.Name) and child.func.id in ("open", "remove", "unlink", "rename"):
                                                print(f"⚠️  {py}:{node.lineno} check-then-act: {node.test.func.attr}() then {child.func.id}()")
                                                print(f"   Use: atomic operations or try/except")
                                                hits += 1
    if hits:
        print(f"\n⚠️  {hits} potential race condition(s). Use atomic file operations.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
