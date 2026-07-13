#!/usr/bin/env python3
"""Audit all sys.exit() calls for consistent exit codes (0=ok, 1=error, 2=usage)."""

import ast
import sys
from pathlib import Path

VALID_CODES = {0, 1, 2}

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py") + list(Path("scripts").rglob("*.py")):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == "exit":
                    if node.args:
                        if isinstance(node.args[0], ast.Constant):
                            code = node.args[0].value
                            if code not in VALID_CODES:
                                print(f"⚠️  {py}:{node.lineno} non-standard exit code: {code}")
                                hits += 1
                        elif isinstance(node.args[0], ast.Name):
                            print(f"⚠️  {py}:{node.lineno} variable exit code (audit manually)")
                            hits += 1
    if hits:
        print(f"\\n❌ {hits} non-standard sys.exit() call(s).")
        return 1
    print("✅ All exit codes are standard (0, 1, 2).")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
