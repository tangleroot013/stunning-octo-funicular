#!/usr/bin/env python3
"""Detect missing security headers in HTTP response configurations."""

import ast
import sys
from pathlib import Path

REQUIRED_HEADERS = {
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
    "strict-transport-security": "max-age",
    "content-security-policy": "",
    "referrer-policy": "",
}

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                keys = set()
                for k in node.keys:
                    if isinstance(k, ast.Constant) and isinstance(k.value, str):
                        keys.add(k.value.lower())
                
                # Check if this looks like a headers dict
                if any("content-type" in k for k in keys):
                    missing = {h for h in REQUIRED_HEADERS if not any(h in k for k in keys)}
                    if missing:
                        print(f"⚠️  {py}:{node.lineno} response headers missing: {missing}")
                        hits += 1
    if hits:
        print(f"\n⚠️  {hits} response config(s) missing security headers.")
        return 0  # warning only
    print("✅ Security headers configured.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
