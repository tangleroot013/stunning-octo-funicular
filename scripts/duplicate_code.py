#!/usr/bin/env python3
"""Simple AST-based duplicate function body detector across src/."""

import ast
import hashlib
from collections import defaultdict
from pathlib import Path

def scan() -> None:
    bodies = defaultdict(list)
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                body = ast.dump(node.body, annotate_fields=False)
                digest = hashlib.sha256(body.encode()).hexdigest()[:12]
                bodies[digest].append(f"{py}:{node.name}")
    dups = {k: v for k, v in bodies.items() if len(v) > 1}
    if dups:
        print(f"⚠️  {len(dups)} duplicate function body hash(es) found:")
        for h, locs in dups.items():
            print(f"   [{h}] {', '.join(locs)}")
    else:
        print("✅ No duplicate function bodies detected.")

if __name__ == "__main__":
    scan()
