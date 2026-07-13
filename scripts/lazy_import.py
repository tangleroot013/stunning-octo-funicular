#!/usr/bin/env python3
"""Audit src/ for eager heavy imports that could be deferred to function scope."""

import ast
from pathlib import Path

HEAVY = {"pandas", "numpy", "tensorflow", "torch", "sklearn", "django", "flask", "sqlalchemy", "requests"}

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                for alias in (node.names if isinstance(node, ast.Import) else [node]):
                    name = getattr(alias, "name", getattr(alias, "asname", "")) or ""
                    if any(h in name for h in HEAVY):
                        if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                            print(f"⚠️  {py}:{node.lineno} heavy top-level import: {node.module}")
                            hits += 1
    if hits:
        print(f"\n❌ {hits} eager heavy import(s). Consider moving to function scope.")
        return 1
    print("✅ No eager heavy imports detected.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(audit())
