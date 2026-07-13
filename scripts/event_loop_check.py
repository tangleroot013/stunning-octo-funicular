#!/usr/bin/env python3
"""Detect unawaited coroutines and bare asyncio.create_task calls."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for create_task without await
                if isinstance(node.func, ast.Attribute) and node.func.attr == "create_task":
                    parent = None
                    # Naive parent check
                    print(f"⚠️  {py}:{node.lineno} asyncio.create_task() — ensure result is tracked")
                    hits += 1
            # Check for async def that returns coroutine without await
            if isinstance(node, ast.Return):
                if isinstance(node.value, ast.Call):
                    if isinstance(node.value.func, ast.Name) and node.value.func.id == "asyncio":
                        print(f"⚠️  {py}:{node.lineno} returning coroutine object without await")
                        hits += 1
    if hits:
        print(f"\n❌ {hits} potential event loop leak(s).")
        return 1
    print("✅ No obvious event loop issues.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
