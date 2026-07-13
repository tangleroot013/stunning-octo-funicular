#!/usr/bin/env python3
"""Detect N+1 query patterns in SQLAlchemy-like ORM code via AST."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Attribute) and child.func.attr in ("query", "filter", "all", "first"):
                            print(f"⚠️  {py}:{node.lineno} possible N+1: loop + query")
                            hits += 1
                            break
    if hits:
        print(f"\n❌ {hits} potential N+1 query pattern(s). Consider eager loading.")
        return 1
    print("✅ No obvious N+1 patterns.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
