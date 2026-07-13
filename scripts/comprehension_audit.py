#!/usr/bin/env python3
"""Flag nested comprehensions (>2 levels) and those with side effects."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                depth = 1
                for gen in node.generators:
                    for if_clause in gen.ifs:
                        depth += 1
                
                # Check for side effects in comprehension body
                for child in ast.walk(node.elt):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name) and child.func.id in ("print", "append", "extend"):
                            print(f"🚨 {py}:{node.lineno} side effect in comprehension")
                            hits += 1
                
                if depth > 2:
                    print(f"⚠️  {py}:{node.lineno} nested comprehension depth {depth}")
                    hits += 1
    if hits:
        print(f"\n⚠️  {hits} comprehension issue(s).")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
