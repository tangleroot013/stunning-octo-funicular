#!/usr/bin/env python3
"""Enforce test file naming: test_*.py and function naming: test_*."""

import ast
import sys
from pathlib import Path

def check() -> int:
    fails = 0
    for py in Path("tests").rglob("*.py"):
        if not py.name.startswith("test_"):
            print(f"❌ {py.name} must start with 'test_'")
            fails += 1
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith("test_") and not re.match(r"test_[a-z_][a-z0-9_]*$", node.name):
                    print(f"⚠️  {py}:{node.name} naming convention off")
                if not node.name.startswith("_") and not node.name.startswith("test_") and not node.name.startswith("fixture"):
                    print(f"❌ {py}:{node.name} must start with 'test_' or 'fixture_'")
                    fails += 1
    print(f"\\n{'✅ All tests properly named' if fails == 0 else f'❌ {fails} naming issue(s)'}")
    return fails

if __name__ == "__main__":
    import re
    sys.exit(check())
