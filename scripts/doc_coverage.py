#!/usr/bin/env python3
"""Report docstring coverage for public functions and classes in src/."""

import ast
from pathlib import Path

def scan() -> None:
    total = covered = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not node.name.startswith("_"):
                    total += 1
                    if ast.get_docstring(node):
                        covered += 1
    pct = (covered / total * 100) if total else 0
    print(f"📖 Doc coverage: {pct:.1f}% ({covered}/{total})")
    if pct < 80:
        print("⚠️  Consider adding docstrings to public APIs.")

if __name__ == "__main__":
    scan()
