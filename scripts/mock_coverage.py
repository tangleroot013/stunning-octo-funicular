#!/usr/bin/env python3
"""Detect untested mock assertions by scanning test files for unused mocks."""

import ast
from pathlib import Path

def scan() -> None:
    for py in Path("tests").rglob("*.py"):
        tree = ast.parse(py.read_text())
        calls = set()
        asserts = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr in ("assert_called", "assert_called_once", "assert_called_with"):
                    asserts.add(node.func.value.id if isinstance(node.func.value, ast.Name) else None)
                if isinstance(node.func, ast.Attribute) and node.func.attr == "Mock":
                    if isinstance(node.func.value, ast.Name):
                        calls.add(node.func.value.id)
        untested = calls - asserts
        if untested:
            print(f"⚠️  {py}: mocks without assertions: {untested}")

if __name__ == "__main__":
    scan()
