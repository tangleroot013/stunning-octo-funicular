#!/usr/bin/env python3
"""Validate FastAPI endpoint function signatures match their docstring param descriptions."""

import ast
import re
import sys
from pathlib import Path

def check() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                # Check if it's a route handler (has route decorator)
                is_route = any(
                    isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr in ("get", "post", "put", "delete", "patch")
                    for d in node.decorator_list
                )
                if not is_route:
                    continue
                
                doc = ast.get_docstring(node)
                if not doc:
                    print(f"❌ {py}:{node.name} — no docstring")
                    hits += 1
                    continue
                
                # Extract param names from signature
                sig_params = {a.arg for a in node.args.args if a.arg not in ("self", "cls", "request")}
                # Extract param names from docstring (naive: look for :param lines)
                doc_params = set(re.findall(r":param\\s+(\\w+):", doc))
                
                missing = sig_params - doc_params
                extra = doc_params - sig_params
                if missing:
                    print(f"⚠️  {py}:{node.name} undocumented params: {missing}")
                    hits += 1
                if extra:
                    print(f"⚠️  {py}:{node.name} stale doc params: {extra}")
                    hits += 1
                if not missing and not extra:
                    print(f"✅ {py}:{node.name}")
    
    if hits:
        print(f"\\n❌ {hits} contract violation(s).")
        return 1
    print("✅ All API endpoints have complete docstrings.")
    return 0

if __name__ == "__main__":
    sys.exit(check())
