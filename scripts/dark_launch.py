#!/usr/bin/env python3
"""Dark launch validator: verify shadow traffic routing and result comparison logic."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Look for shadow/duplicate call patterns
                calls = [n for n in ast.walk(node) if isinstance(n, ast.Call)]
                func_names = []
                for call in calls:
                    if isinstance(call.func, ast.Name):
                        func_names.append(call.func.id)
                    elif isinstance(call.func, ast.Attribute):
                        func_names.append(call.func.attr)
                
                # Check for old vs new function pattern
                if any("old" in f for f in func_names) and any("new" in f for f in func_names):
                    has_compare = any(
                        isinstance(n, ast.Compare) and any(isinstance(o, (ast.Eq, ast.NotEq)) for o in n.ops)
                        for n in ast.walk(node)
                    )
                    if not has_compare:
                        print(f"⚠️  {py}:{node.lineno} dark launch without result comparison")
                        hits += 1
                    else:
                        print(f"✅ {py}:{node.lineno} dark launch with comparison")
    if hits:
        print(f"\n⚠️  {hits} dark launch(es) without comparison. Add result diff logging.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
