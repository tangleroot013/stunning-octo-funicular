#!/usr/bin/env python3
"""Detect hardcoded TLS/SSL verification disabled (verify=False) in HTTP clients."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.keyword):
                if node.arg == "verify":
                    if isinstance(node.value, ast.Constant) and node.value.value == False:
                        print(f"🚨 {py}:{node.lineno} TLS verification DISABLED: verify=False")
                        print(f"   This exposes the application to MITM attacks.")
                        hits += 1
            # Check for ssl._create_unverified_context
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if "unverified" in node.func.attr.lower():
                        print(f"🚨 {py}:{node.lineno} unverified SSL context: {node.func.attr}")
                        hits += 1
    if hits:
        print(f"\n❌ {hits} TLS verification bypass(s). Never disable in production.")
        return 1
    print("✅ TLS verification enforced.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
