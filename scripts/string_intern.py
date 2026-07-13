#!/usr/bin/env python3
"""Detect repeated string literals across src/ that could benefit from interning."""

import ast
from collections import Counter
from pathlib import Path
import sys

def audit() -> None:
    literals = Counter()
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if len(node.value) > 3 and node.value.isidentifier():
                    literals[node.value] += 1
    
    dupes = {k: v for k, v in literals.items() if v > 5}
    if dupes:
        print(f"⚠️  {len(dupes)} repeated string literals (consider sys.intern() or constants):")
        for s, count in dupes.most_common(10):
            print(f"   '{s}': {count} occurrences")
    else:
        print("✅ No heavily repeated string literals detected.")

if __name__ == "__main__":
    audit()
