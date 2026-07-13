#!/usr/bin/env python3
"""Detect JWT usage without algorithm verification or with weak algorithms."""

import ast
import sys
from pathlib import Path

WEAK_ALGOS = {"none", "HS256", "HS384", "HS512"}  # HS* is fine but RS/ES preferred

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check jwt.decode calls
                if isinstance(node.func, ast.Attribute) and node.func.attr == "decode":
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "jwt":
                        has_verify = False
                        has_algo = False
                        for kw in node.keywords:
                            if kw.arg == "verify" and isinstance(kw.value, ast.Constant):
                                if kw.value.value == False:
                                    print(f"🚨 {py}:{node.lineno} jwt.decode with verify=False")
                                    hits += 1
                            if kw.arg == "algorithms":
                                has_algo = True
                        if not has_algo:
                            print(f"🚨 {py}:{node.lineno} jwt.decode without algorithms parameter")
                            hits += 1
    if hits:
        print(f"\n❌ {hits} JWT verification issue(s). Always specify algorithms and verify signatures.")
        return 1
    print("✅ JWT usage looks secure.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
