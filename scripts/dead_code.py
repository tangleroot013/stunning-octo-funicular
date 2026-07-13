#!/usr/bin/env python3
"""Find public functions/classes defined in src/ but never imported anywhere."""

import ast
import sys
from collections import defaultdict
from pathlib import Path

def scan() -> int:
    defined = defaultdict(list)   # name -> [file, ...]
    imported = set()
    
    for py in Path("src").rglob("*.py"):
        mod = ".".join(py.relative_to("src").with_suffix("").parts)
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_"):
                    defined[node.name].append(f"{mod}:{node.name}")
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported.add(alias.name)
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.name)
    
    for py in Path("tests").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported.add(alias.name)
    
    dead = {k: v for k, v in defined.items() if k not in imported and len(v) == 1}
    if dead:
        print(f"⚠️  Potentially dead code ({len(dead)} symbol(s)):")
        for name, locs in dead.items():
            for loc in locs:
                print(f"   {loc}")
        return 1
    print("✅ No obviously dead public symbols.")
    return 0

if __name__ == "__main__":
    sys.exit(scan())
