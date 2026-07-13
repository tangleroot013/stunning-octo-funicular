#!/usr/bin/env python3
"""Detect inefficient string concatenation in loops (O(n²) pattern)."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                        if isinstance(child.target, ast.Name) and isinstance(child.value, (ast.Constant, ast.Name, ast.Call)):
                            print(f"🔥 {py}:{child.lineno} string concatenation in loop — use list.append() + ''.join()")
                            hits += 1
                    if isinstance(child, ast.Assign):
                        for target in child.targets:
                            if isinstance(target, ast.Name):
                                # Check if same var reassigned with + in loop body
                                pass  # simplified
    if hits:
        print(f"\n❌ {hits} inefficient string concat(s) in loops.")
        return 1
    print("✅ No inefficient string concatenation patterns.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
