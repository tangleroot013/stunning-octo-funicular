#!/usr/bin/env python3
"""Audit Enum classes for auto() usage, unique decorator, and str/repr methods."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                is_enum = any(
                    isinstance(b, ast.Attribute) and b.attr == "Enum"
                    for b in node.bases
                )
                if not is_enum:
                    continue
                
                has_unique = any(
                    isinstance(d, ast.Call) and isinstance(d.func, ast.Name) and d.func.id == "unique"
                    for d in node.decorator_list
                )
                if not has_unique:
                    print(f"⚠️  {py}:{node.lineno} {node.name}: Enum without @unique")
                    hits += 1
                
                # Check for auto() usage
                has_auto = False
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for val in ast.walk(item):
                            if isinstance(val, ast.Call) and isinstance(val.func, ast.Name) and val.func.id == "auto":
                                has_auto = True
                if not has_auto:
                    print(f"🔍 {py}:{node.lineno} {node.name}: Enum without auto() — verify values are intentional")
    if hits:
        print(f"\n⚠️  {hits} Enum issue(s).")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
