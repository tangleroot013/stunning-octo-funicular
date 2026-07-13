#!/usr/bin/env python3
"""Detect nested if-else that could be flattened with guard clauses."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Check if it's the first statement in a function and has else
                if node.orelse and isinstance(node.orelse[0], ast.If):
                    print(f"⚠️  {py}:{node.lineno} nested if-else chain — consider guard clauses")
                    hits += 1
    if hits:
        print(f"\n⚠️  {hits} nested if-else chain(s). Flatten with early returns.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
