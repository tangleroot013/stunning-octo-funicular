#!/usr/bin/env python3
"""Detect deeply stacked decorators (>3) that may impact readability and performance."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if len(node.decorator_list) > 3:
                    names = []
                    for d in node.decorator_list:
                        if isinstance(d, ast.Name):
                            names.append(d.id)
                        elif isinstance(d, ast.Attribute):
                            names.append(d.attr)
                        elif isinstance(d, ast.Call):
                            if isinstance(d.func, ast.Name):
                                names.append(d.func.id)
                            elif isinstance(d.func, ast.Attribute):
                                names.append(d.func.attr)
                    print(f"⚠️  {py}:{node.lineno} {node.name}: {len(node.decorator_list)} decorators ({', '.join(names)})")
                    hits += 1
    if hits:
        print(f"\n❌ {hits} function(s) with >3 decorators. Consider composition.")
        return 1
    print("✅ Decorator stacks reasonable.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
