#!/usr/bin/env python3
"""Flag complex lambdas (>1 expression or >80 chars) that should be def functions."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        text = py.read_text()
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.Lambda):
                # Check line length
                lines = text.splitlines()
                if node.lineno <= len(lines):
                    line = lines[node.lineno - 1]
                    if len(line) > 80:
                        print(f"⚠️  {py}:{node.lineno} lambda exceeds 80 chars — use def")
                        hits += 1
                        continue
                
                # Check complexity (nested lambdas or multiple ops)
                body_complexity = sum(1 for _ in ast.walk(node.body) if isinstance(_, (ast.Call, ast.BinOp, ast.BoolOp, ast.Compare)))
                if body_complexity > 3:
                    print(f"⚠️  {py}:{node.lineno} complex lambda ({body_complexity} ops) — use def")
                    hits += 1
    if hits:
        print(f"\n❌ {hits} lambda(s) too complex. Extract to named functions.")
        return 1
    print("✅ Lambda usage clean.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
