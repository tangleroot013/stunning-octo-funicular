#!/usr/bin/env python3
"""Detect eval(), exec(), compile(), and __import__() usage in source code."""

import ast
import sys
from pathlib import Path

DANGEROUS = {"eval", "exec", "compile", "__import__"}

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in DANGEROUS:
                    print(f"🚨 {py}:{node.lineno} dangerous call: {node.func.id}()")
                    hits += 1
                if isinstance(node.func, ast.Attribute) and node.func.attr == "eval":
                    print(f"🚨 {py}:{node.lineno} dangerous call: eval() via attribute")
                    hits += 1
    if hits:
        print(f"\n❌ {hits} dangerous dynamic execution call(s). Use ast.literal_eval or json.loads.")
        return 1
    print("✅ No eval/exec/compile/__import__ detected.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
