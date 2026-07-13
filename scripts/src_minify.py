#!/usr/bin/env python3
"""Strip comments and docstrings from src/ to estimate 'true' code size."""

import ast
from pathlib import Path

def minify(source: str) -> str:
    tree = ast.parse(source)
    lines = source.splitlines()
    to_remove = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Expr,)) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            for i in range(node.lineno - 1, getattr(node, "end_lineno", node.lineno)):
                to_remove.add(i)
        if isinstance(node, ast.FunctionDef):
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
                for i in range(node.body[0].lineno - 1, getattr(node.body[0], "end_lineno", node.body[0].lineno)):
                    to_remove.add(i)
    result = [l for i, l in enumerate(lines) if i not in to_remove and not l.strip().startswith("#")]
    return "\\n".join(result)

def analyze() -> None:
    original = 0
    stripped = 0
    for py in Path("src").rglob("*.py"):
        src = py.read_text()
        mini = minify(src)
        original += len(src)
        stripped += len(mini)
    pct = (1 - stripped / original) * 100 if original else 0
    print(f"📉 src/ minified: {original} → {stripped} bytes ({pct:.1f}% comment/docstring overhead)")

if __name__ == "__main__":
    analyze()
