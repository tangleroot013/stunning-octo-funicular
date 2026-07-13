#!/usr/bin/env python3
"""Audit @final decorator usage on classes and methods that should not be overridden."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if any(isinstance(b, ast.Name) and b.id == "ABC" for b in node.bases):
                    # Abstract base classes should mark concrete methods @final
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name != "__init__":
                            has_final = any(
                                isinstance(d, ast.Name) and d.id == "final"
                                for d in item.decorator_list
                            )
                            if not has_final and not item.name.startswith("_"):
                                print(f"⚠️  {py}:{item.lineno} {node.name}.{item.name}: concrete method not @final")
                                hits += 1
    if hits:
        print(f"\n⚠️  {hits} concrete method(s) in ABC without @final.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
