#!/usr/bin/env python3
"""Detect exception handlers that may leak sensitive info in production responses."""

import ast
import sys
from pathlib import Path

LEAKY_PATTERNS = {"traceback", "exc_info", "sys.exc_info", "format_exc", "print_exc"}

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Attribute):
                            if child.func.attr in ("json", "response", "send", "write"):
                                # Check if exception info is passed
                                for arg in child.args:
                                    if isinstance(arg, ast.Name) and arg.id in ("e", "exc", "error"):
                                        print(f"🚨 {py}:{child.lineno} exception object sent to client: {arg.id}")
                                        hits += 1
                    if isinstance(child, ast.Call):
                        func_name = ""
                        if isinstance(child.func, ast.Name):
                            func_name = child.func.id
                        elif isinstance(child.func, ast.Attribute):
                            func_name = child.func.attr
                        if func_name in ("format_exc", "print_exc"):
                            print(f"🚨 {py}:{child.lineno} traceback exposed: {func_name}()")
                            hits += 1
    if hits:
        print(f"\n❌ {hits} exception info leak(s). Return generic messages to clients.")
        return 1
    print("✅ No exception info leaks detected.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
