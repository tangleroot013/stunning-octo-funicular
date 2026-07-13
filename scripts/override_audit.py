#!/usr/bin/env python3
"""Detect method overrides that don't call super() when parent is non-trivial."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if class has bases
                if not node.bases:
                    continue
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        # Check for super() call
                        has_super = False
                        for child in ast.walk(item):
                            if isinstance(child, ast.Call):
                                if isinstance(child.func, ast.Name) and child.func.id == "super":
                                    has_super = True
                                elif isinstance(child.func, ast.Attribute):
                                    if isinstance(child.func.value, ast.Call) and isinstance(child.func.value.func, ast.Name) and child.func.value.func.id == "super":
                                        has_super = True
                        if not has_super and item.name != "__init__":
                            print(f"⚠️  {py}:{item.lineno} {node.name}.{item.name} overrides without super()")
                            hits += 1
    if hits:
        print(f"\n⚠️  {hits} override(s) without super(). Review for correctness.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
