#!/usr/bin/env python3
"""Detect magic numbers in source code (exclude 0, 1, -1, common HTTP codes)."""

import ast
import sys
from pathlib import Path

ALLOWED = {0, 1, -1, 2, 10, 100, 200, 201, 204, 301, 302, 400, 401, 403, 404, 500, 502, 503, 60, 3600, 86400, 1024, 1000}

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if node.value not in ALLOWED and abs(node.value) > 1:
                    # Skip if part of a default arg (often valid)
                    parent = None  # naive
                    print(f"⚠️  {py}:{node.lineno} magic number: {node.value}")
                    hits += 1
    if hits:
        print(f"\n❌ {hits} magic number(s). Extract to named constants.")
        return 1
    print("✅ No magic numbers detected.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
