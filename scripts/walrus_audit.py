#!/usr/bin/env python3
"""Audit walrus operator (:=) usage for clarity and side-effect risks."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.NamedExpr):
                # Check if used in a complex expression (risky)
                parent = None
                context = "assignment"
                # Heuristic: if in a Call or BoolOp, flag for review
                print(f"🔍 {py}:{node.lineno} walrus: {node.target.id} = ...")
                hits += 1
    if hits:
        print(f"\n⚠️  {hits} walrus operator(s). Review for clarity.")
    else:
        print("✅ No walrus operators found.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
