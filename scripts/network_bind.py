#!/usr/bin/env python3
"""Detect services binding to 0.0.0.0 or wildcard interfaces."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if node.value in ("0.0.0.0", "::", "", "*"):
                    # Check context
                    print(f"🚨 {py}:{node.lineno} wildcard bind: '{node.value}'")
                    print(f"   Use 127.0.0.1 or specific interface unless intentional")
                    hits += 1
            if isinstance(node, ast.keyword):
                if node.arg in ("host", "bind", "interface"):
                    if isinstance(node.value, ast.Constant) and node.value.value in ("0.0.0.0", "::", "", "*"):
                        print(f"🚨 {py}:{node.lineno} wildcard bind via keyword: {node.arg}='{node.value.value}'")
                        hits += 1
    if hits:
        print(f"\n❌ {hits} wildcard bind(s). Restrict to localhost unless public service.")
        return 1
    print("✅ Network bindings restricted.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
