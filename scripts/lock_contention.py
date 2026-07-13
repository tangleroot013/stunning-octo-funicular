#!/usr/bin/env python3
"""Detect threading.Lock and asyncio.Lock usage patterns that may cause deadlocks."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.With):
                locks = [i for i in node.items if isinstance(i.context_expr, ast.Call)]
                if len(locks) > 1:
                    names = []
                    for i in locks:
                        if isinstance(i.context_expr.func, ast.Name):
                            names.append(i.context_expr.func.id)
                        elif isinstance(i.context_expr.func, ast.Attribute):
                            names.append(i.context_expr.func.attr)
                    if "Lock" in names or "lock" in names:
                        print(f"🚨 {py}:{node.lineno} nested locks (deadlock risk): {names}")
                        hits += 1
            # Check for acquire without try/finally
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == "acquire":
                    parent = None  # naive check
                    print(f"⚠️  {py}:{node.lineno} lock.acquire() — verify try/finally wrapper")
                    hits += 1
    if hits:
        print(f"\\n❌ {hits} potential lock contention issue(s).")
        return 1
    print("✅ No obvious lock hazards.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
