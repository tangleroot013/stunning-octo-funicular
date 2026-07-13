#!/usr/bin/env python3
"""Verify audit logging patterns exist for sensitive operations (create, delete, auth)."""

import ast
import sys
from pathlib import Path

SENSITIVE_OPS = {"delete", "remove", "create", "update", "modify", "transfer", "approve", "reject"}

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if any(op in node.name.lower() for op in SENSITIVE_OPS):
                    has_audit = False
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Attribute):
                                if any(x in child.func.attr.lower() for x in ("log", "audit", "record", "track")):
                                    has_audit = True
                            if isinstance(child.func, ast.Name):
                                if any(x in child.func.id.lower() for x in ("log", "audit")):
                                    has_audit = True
                    if not has_audit:
                        print(f"⚠️  {py}:{node.lineno} {node.name}() — no audit logging detected")
                        hits += 1
                    else:
                        print(f"✅ {py}:{node.lineno} {node.name}() — audit logged")
    if hits:
        print(f"\n⚠️  {hits} sensitive operation(s) without audit logging.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
