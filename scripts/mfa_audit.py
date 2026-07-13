#!/usr/bin/env python3
"""Detect authentication code without MFA/2FA enforcement patterns."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if any(x in node.name.lower() for x in ("login", "auth", "signin", "authenticate")):
                    has_mfa = False
                    for child in ast.walk(node):
                        if isinstance(child, ast.Name):
                            if any(x in child.id.lower() for x in ("mfa", "totp", "otp", "2fa", "twofactor")):
                                has_mfa = True
                        if isinstance(child, ast.Constant) and isinstance(child.value, str):
                            if any(x in child.value.lower() for x in ("mfa", "2fa", "totp")):
                                has_mfa = True
                    if not has_mfa:
                        print(f"⚠️  {py}:{node.lineno} {node.name}() — no MFA pattern detected")
                        hits += 1
                    else:
                        print(f"✅ {py}:{node.lineno} {node.name}() — MFA present")
    if hits:
        print(f"\n⚠️  {hits} auth function(s) without MFA. Consider enforcing 2FA.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
