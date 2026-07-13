#!/usr/bin/env python3
"""Flag functions with excessive nesting depth (>4) that hurt readability."""

import ast
import sys
from pathlib import Path

def max_nesting(node: ast.AST, depth: int = 0) -> int:
    body_nodes = []
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        body_nodes = node.body
    elif isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.ExceptHandler)):
        body_nodes = node.body + (node.orelse if hasattr(node, "orelse") else [])
    
    if not body_nodes:
        return depth
    
    return max(max_nesting(child, depth + 1) for child in ast.iter_child_nodes(node) if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.FunctionDef, ast.ExceptHandler)))

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                nesting = max_nesting(node)
                if nesting > 4:
                    print(f"🔥 {py}:{node.lineno} {node.name} nests {nesting} deep")
                    hits += 1
                elif nesting > 3:
                    print(f"⚠️  {py}:{node.lineno} {node.name} nests {nesting} deep")
                    hits += 1
    if hits:
        print(f"\n❌ {hits} function(s) with excessive nesting. Consider early returns.")
        return 1
    print("✅ Nesting depth acceptable.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
