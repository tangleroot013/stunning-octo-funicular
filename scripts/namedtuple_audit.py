#!/usr/bin/env python3
"""Detect collections.namedtuple usage that should be @dataclass or typing.NamedTuple."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == "namedtuple":
                        print(f"⚠️  {py}:{node.lineno} collections.namedtuple — use @dataclass(frozen=True) or typing.NamedTuple")
                        hits += 1
            if isinstance(node, ast.ImportFrom):
                if node.module == "collections":
                    for alias in node.names:
                        if alias.name == "namedtuple":
                            print(f"⚠️  {py}:{node.lineno} imports namedtuple — modernize")
                            hits += 1
    if hits:
        print(f"\n❌ {hits} namedtuple usage(s). Migrate to dataclass.")
        return 1
    print("✅ No namedtuple usage.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
