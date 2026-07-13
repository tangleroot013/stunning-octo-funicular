#!/usr/bin/env python3
"""Audit Union[X, Y] vs X | Y syntax for Python 3.10+ compatibility."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Subscript):
                if isinstance(node.value, ast.Name) and node.value.id == "Union":
                    print(f"⚠️  {py}:{node.lineno} Union[X, Y] — use X | Y (Python 3.10+)")
                    hits += 1
                if isinstance(node.value, ast.Name) and node.value.id == "Optional":
                    print(f"⚠️  {py}:{node.lineno} Optional[X] — use X | None (Python 3.10+)")
                    hits += 1
    if hits:
        print(f"\n❌ {hits} outdated typing construct(s). Modernize to | syntax.")
        return 1
    print("✅ All unions use modern syntax.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
