#!/usr/bin/env python3
"""Detect import aliases that deviate from PEP 8 or project conventions."""

import ast
import sys
from pathlib import Path

CONVENTIONS = {
    "numpy": "np",
    "pandas": "pd",
    "matplotlib.pyplot": "plt",
    "tensorflow": "tf",
    "torch": "pt",
}

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in CONVENTIONS:
                        expected = CONVENTIONS[alias.name]
                        if alias.asname and alias.asname != expected:
                            print(f"⚠️  {py}:{node.lineno} {alias.name} aliased as '{alias.asname}' (convention: '{expected}')")
                            hits += 1
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    full = f"{node.module}.{alias.name}" if node.module else alias.name
                    if full in CONVENTIONS:
                        expected = CONVENTIONS[full]
                        if alias.asname and alias.asname != expected:
                            print(f"⚠️  {py}:{node.lineno} {full} aliased as '{alias.asname}' (convention: '{expected}')")
                            hits += 1
    if hits:
        print(f"\n❌ {hits} non-standard alias(es).")
        return 1
    print("✅ All aliases follow conventions.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
