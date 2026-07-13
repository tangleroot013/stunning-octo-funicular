#!/usr/bin/env python3
"""Detect session/cookie configuration without secure, httponly, samesite flags."""

import ast
import sys
from pathlib import Path

REQUIRED_FLAGS = {"secure", "httponly", "samesite"}

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.keyword):
                if node.arg == "session_cookie":
                    print(f"🔍 {py}:{node.lineno} session configuration detected")
                if node.arg in ("cookie", "session"):
                    if isinstance(node.value, ast.Dict):
                        keys = {k.value for k in node.value.keys if isinstance(k, ast.Constant)}
                        missing = REQUIRED_FLAGS - keys
                        if missing:
                            print(f"🚨 {py}:{node.lineno} session missing flags: {missing}")
                            hits += 1
    if hits:
        print(f"\n❌ {hits} session config(s) missing security flags.")
        return 1
    print("✅ Session security flags present.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
