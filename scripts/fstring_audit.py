#!/usr/bin/env python3
"""Audit f-string formatting directives for potential locale/decimal issues."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.JoinedStr):
                for value in node.values:
                    if isinstance(value, ast.FormattedValue):
                        if value.format_spec:
                            spec = ast.unparse(value.format_spec)
                            if ":.2f" in spec or ":.0f" in spec:
                                # Check if used for currency/price
                                print(f"🔍 {py}:{node.lineno} f-string float format — verify locale safety")
                                hits += 1
    if hits:
        print(f"\n⚠️  {hits} f-string float format(s). Consider Decimal for currency.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
