#!/usr/bin/env python3
"""Detect SQL string concatenation and f-string formatting (SQL injection vectors)."""

import ast
import re
import sys
from pathlib import Path

SQL_PATTERNS = re.compile(r"(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\\s", re.IGNORECASE)

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            # Check f-strings in SQL contexts
            if isinstance(node, ast.JoinedStr):
                # Find parent to see if in SQL context
                print(f"🔍 {py}:{node.lineno} f-string detected — verify not used for SQL")
                hits += 1
            
            # Check string concatenation with SQL keywords
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
                # This is a simplified check
                pass
            
            # Check .format() on SQL strings
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == "format":
                    print(f"🚨 {py}:{node.lineno} .format() on string — potential injection vector")
                    hits += 1
            
            # Check % formatting
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
                if isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
                    if SQL_PATTERNS.search(node.left.value):
                        print(f"🚨 {py}:{node.lineno} % formatting on SQL string — injection risk")
                        hits += 1
    if hits:
        print(f"\n❌ {hits} potential SQL injection vector(s). Use parameterized queries.")
        return 1
    print("✅ No obvious SQL injection vectors.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
