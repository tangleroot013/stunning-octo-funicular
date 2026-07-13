#!/usr/bin/env python3
"""Check __init__.py files for namespace pollution (imports that shouldn't be public)."""

import ast
import sys
from pathlib import Path

def check() -> int:
    hits = 0
    for init in Path("src").rglob("__init__.py"):
        tree = ast.parse(init.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname or alias.name
                    if name.startswith("_"):
                        continue
                    # Heuristic: if it's a deep import, it's probably pollution
                    if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                        if "." in node.module and not node.module.startswith("src"):
                            print(f"⚠️  {init}: imports external '{node.module}' at top level")
                            hits += 1
    if hits:
        print(f"\\n❌ {hits} potential namespace pollution(s). Use __all__ or lazy imports.")
        return 1
    print("✅ __init__.py namespace looks clean.")
    return 0

if __name__ == "__main__":
    sys.exit(check())
