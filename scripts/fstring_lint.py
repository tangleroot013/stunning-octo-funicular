#!/usr/bin/env python3
"""Flag overly complex f-strings (>3 expressions) that hurt readability."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.JoinedStr):
                expr_count = sum(1 for v in node.values if isinstance(v, ast.FormattedValue))
                if expr_count > 3:
                    print(f"⚠️  {py}:{node.lineno} f-string with {expr_count} expressions (consider .format() or template)")
                    hits += 1
    if hits:
        print(f"\\n❌ {hits} overly complex f-string(s).")
        return 1
    print("✅ All f-strings are readable.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
