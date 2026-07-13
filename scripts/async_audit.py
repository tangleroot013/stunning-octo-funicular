#!/usr/bin/env python3
"""Detect sync I/O inside async functions (blocks the event loop)."""

import ast
import sys
from pathlib import Path

BLOCKING = {"open", "read", "write", "sleep", "requests.get", "requests.post", "urllib.request.urlopen", "subprocess.run", "subprocess.check_output"}

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        name = ""
                        if isinstance(child.func, ast.Name):
                            name = child.func.id
                        elif isinstance(child.func, ast.Attribute):
                            name = child.func.attr
                        if name in BLOCKING:
                            print(f"🚨 {py}:{child.lineno} blocking '{name}' inside async '{node.name}'")
                            hits += 1
    if hits:
        print(f"\n❌ {hits} blocking call(s) in async functions. Use aiohttp, aiofiles, asyncio.sleep, etc.")
        return 1
    print("✅ No blocking calls in async functions.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
