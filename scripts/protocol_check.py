#!/usr/bin/env python3
"""Detect typing.Protocol definitions and verify runtime checkable decorators."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                is_protocol = any(
                    isinstance(base, ast.Attribute) and base.attr == "Protocol"
                    for base in node.bases
                )
                if is_protocol:
                    has_runtime = any(
                        isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr == "runtime_checkable"
                        for d in node.decorator_list
                    )
                    if not has_runtime:
                        print(f"⚠️  {py}:{node.lineno} {node.name}: Protocol without @runtime_checkable")
                        hits += 1
                    else:
                        print(f"✅ {py}:{node.lineno} {node.name}: runtime-checkable Protocol")
    if hits:
        print(f"\n⚠️  {hits} Protocol(s) missing @runtime_checkable.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
