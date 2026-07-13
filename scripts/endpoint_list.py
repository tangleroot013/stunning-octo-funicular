#!/usr/bin/env python3
"""Extract and list all FastAPI endpoints from src/ routers."""

import ast
import sys
from pathlib import Path

def extract() -> int:
    endpoints = []
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr in ("get", "post", "put", "delete", "patch"):
                    path = ""
                    for kw in node.keywords:
                        if kw.arg == "path" and isinstance(kw.value, ast.Constant):
                            path = kw.value.value
                    endpoints.append(f"{node.func.attr.upper():6} {path}")
    if endpoints:
        print("\n".join(sorted(set(endpoints))))
    else:
        print("ℹ️  No FastAPI endpoints found.")
    return 0

if __name__ == "__main__":
    sys.exit(extract())
