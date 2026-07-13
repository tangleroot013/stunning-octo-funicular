#!/usr/bin/env python3
"""Audit __slots__ usage: high-instance-count classes should use slots for memory."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_slots = any(
                    isinstance(item, ast.Assign) and
                    any(isinstance(t, ast.Name) and t.id == "__slots__" for t in item.targets)
                    for item in node.body
                )
                has_dataclass = any(
                    (isinstance(d, ast.Name) and d.id == "dataclass") or
                    (isinstance(d, ast.Call) and isinstance(d.func, ast.Name) and d.func.id == "dataclass")
                    for d in node.decorator_list
                )
                if has_dataclass and not has_slots:
                    print(f"⚠️  {py}:{node.lineno} {node.name}: dataclass without slots=True")
                    hits += 1
    if hits:
        print(f"\n⚠️  {hits} dataclass(es) missing slots. Add slots=True for memory efficiency.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
