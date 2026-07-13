#!/usr/bin/env python3
"""Detect os.path usage that should be pathlib for cross-platform safety."""

import ast
import sys
from pathlib import Path

OSPATH_FUNCS = {"join", "exists", "isfile", "isdir", "basename", "dirname", "abspath", "realpath"}

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Attribute) and node.value.attr == "path":
                    if isinstance(node.value.value, ast.Name) and node.value.value.id == "os":
                        if node.attr in OSPATH_FUNCS:
                            print(f"⚠️  {py}:{node.lineno} os.path.{node.attr} — consider pathlib.Path")
                            hits += 1
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "os.path":
                        print(f"⚠️  {py}:{node.lineno} imports os.path — prefer pathlib")
                        hits += 1
    if hits:
        print(f"\n❌ {hits} os.path usage(s). Migrate to pathlib.")
        return 1
    print("✅ pathlib usage consistent.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
