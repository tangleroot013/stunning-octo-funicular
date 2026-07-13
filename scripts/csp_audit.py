#!/usr/bin/env python3
"""Audit Content-Security-Policy headers in FastAPI responses for unsafe directives."""

import ast
import sys
from pathlib import Path

UNSAFE = {"unsafe-inline", "unsafe-eval", "*", "data:", "http:"}

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if "Content-Security-Policy" in node.value or "csp" in node.value.lower():
                    for bad in UNSAFE:
                        if bad in node.value:
                            print(f"🚨 {py}:{node.lineno} unsafe CSP directive: '{bad}'")
                            hits += 1
    if hits:
        print(f"\n❌ {hits} unsafe CSP directive(s). Remove 'unsafe-inline', 'unsafe-eval', wildcards.")
        return 1
    print("✅ CSP headers look safe.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
