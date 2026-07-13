#!/usr/bin/env python3
"""Detect network and file operations without timeout parameters."""

import ast
import sys
from pathlib import Path

TIMEOUT_REQUIRED = {"requests.get", "requests.post", "requests.put", "requests.delete", "urllib.request.urlopen", "socket.create_connection"}

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        func_name = f"{node.func.value.id}.{node.func.attr}"
                    elif isinstance(node.func.value, ast.Attribute):
                        func_name = f"{node.func.value.value.id}.{node.func.value.attr}.{node.func.attr}" if isinstance(node.func.value.value, ast.Name) else ""
                
                if func_name in TIMEOUT_REQUIRED:
                    has_timeout = any(k.arg == "timeout" for k in node.keywords)
                    if not has_timeout:
                        print(f"🚨 {py}:{node.lineno} {func_name}() without timeout — hangs forever on failure")
                        hits += 1
    if hits:
        print(f"\n❌ {hits} operation(s) missing timeout. Add timeout=30 or similar.")
        return 1
    print("✅ All network operations have timeouts.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
