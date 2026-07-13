#!/usr/bin/env python3
"""Detect manual comparison of signatures/hashes instead of hmac.compare_digest."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            # Check for == comparison on signature-like variables
            if isinstance(node, ast.Compare):
                if isinstance(node.ops[0], ast.Eq) if node.ops else False:
                    # Check if comparing variables with signature-like names
                    for comparator in [node.left] + list(node.comparators):
                        if isinstance(comparator, ast.Name):
                            if any(x in comparator.id.lower() for x in ("sig", "sign", "hash", "hmac", "token")):
                                print(f"🚨 {py}:{node.lineno} timing-attack vulnerable comparison: '{comparator.id} == ...'")
                                print(f"   Use: hmac.compare_digest({comparator.id}, expected)")
                                hits += 1
    if hits:
        print(f"\n❌ {hits} vulnerable comparison(s). Use hmac.compare_digest() or secrets.compare_digest().")
        return 1
    print("✅ No vulnerable comparisons detected.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
