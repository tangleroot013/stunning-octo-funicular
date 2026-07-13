#!/usr/bin/env python3
"""Detect pickle, yaml.load, and other unsafe deserialization patterns."""

import ast
import sys
from pathlib import Path

UNSAFE = {"pickle", "cPickle", "yaml.load", "marshal.loads", "shelve"}

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ("pickle", "cPickle"):
                        print(f"🚨 {py}:{node.lineno} imports {alias.name} — arbitrary code execution risk")
                        hits += 1
            if isinstance(node, ast.ImportFrom):
                if node.module in ("pickle", "cPickle", "marshal", "shelve"):
                    print(f"🚨 {py}:{node.lineno} imports from {node.module}")
                    hits += 1
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == "load":
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "yaml":
                        print(f"🚨 {py}:{node.lineno} yaml.load() without Loader — use yaml.safe_load()")
                        hits += 1
    if hits:
        print(f"\n❌ {hits} unsafe deserialization pattern(s). Use json, msgpack, or yaml.safe_load().")
        return 1
    print("✅ No unsafe deserialization detected.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
